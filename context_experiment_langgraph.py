"""
Context Engineering with LangGraph
使用 LangGraph 的 StateGraph 來管理三種 context 策略的測試流程

核心概念：
- State: 保存當前句子、策略、模型輸出
- Nodes: run_A / run_B / run_C (各自呼叫 API)
- Edges: 依序執行 A → B → C
- 最後收斂到 END，輸出每個策略的結果
"""

import os
import json
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Literal
from openai import OpenAI
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END

# 載入環境變數
load_dotenv()

# 初始化 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================================
# 1. 定義 State Schema
# ============================================================================

class ContextEngineringState(TypedDict):
    """
    State 保存整個實驗的狀態
    """
    # 輸入
    test_sentence: str
    test_id: int
    
    # 三種 Context 定義
    context_a: str
    context_b: str
    context_c: str
    
    # 每個策略的輸出
    result_a: Dict[str, Any]
    result_b: Dict[str, Any]
    result_c: Dict[str, Any]
    
    # 評分
    scores: Dict[str, float]
    
    # 當前處理階段
    current_step: str


# ============================================================================
# 2. 定義三種 Context 策略
# ============================================================================

CTX_A = """You are a sentiment analyzer.
Extract product info from this review."""

CTX_B = """You are a sentiment analyzer.

Extract the following information from product reviews:
- sentiment: must be "positive", "neutral", or "negative"
- product: the product name (string)
- issue: description of any issues (string, or empty)

Output must be valid JSON format.
Do not include markdown code blocks."""

CTX_C = CTX_B + """

Examples:

Input: "這支耳機音質不錯，但藍牙常常斷線。"
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth connection"}

Input: "The keyboard feels great, but the battery dies too fast."
Output: {"sentiment": "negative", "product": "keyboard", "issue": "battery life"}"""


# ============================================================================
# 3. 輔助函數
# ============================================================================

def call_openai_api(system_prompt: str, user_message: str, model: str = "gpt-4o-mini") -> str:
    """呼叫 OpenAI API"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def clean_json_response(response: str) -> str:
    """清理 markdown code blocks"""
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])
        if response.startswith("json"):
            response = response[4:].strip()
    return response


def score_response(response: str) -> float:
    """評分函數"""
    score = 0.0
    
    try:
        data = json.loads(response)
        score += 0.25  # 有效 JSON
        
        if "sentiment" in data:
            score += 0.25
        if "product" in data:
            score += 0.25
        if "issue" in data:
            score += 0.25
        
        if data.get("sentiment") in ["positive", "neutral", "negative"]:
            score += 0.25
        
        if data.get("product") and data.get("product").strip():
            score += 0.25
    except:
        pass
    
    return min(score, 1.0)


# ============================================================================
# 4. 定義 Node Functions
# ============================================================================

def run_context_a(state: ContextEngineringState) -> ContextEngineringState:
    """
    Node A: 測試 Baseline Context
    """
    print(f"\n🔵 Testing Context A (Baseline) for test #{state['test_id']}...")
    
    response = call_openai_api(state["context_a"], state["test_sentence"])
    cleaned = clean_json_response(response)
    score = score_response(cleaned)
    
    state["result_a"] = {
        "raw_response": response,
        "cleaned_response": cleaned,
        "score": score
    }
    state["scores"]["Context A"] = score
    state["current_step"] = "completed_a"
    
    print(f"   Score: {score:.1%}")
    
    return state


def run_context_b(state: ContextEngineringState) -> ContextEngineringState:
    """
    Node B: 測試 Rules-based Context
    """
    print(f"\n🟢 Testing Context B (Rules-based) for test #{state['test_id']}...")
    
    response = call_openai_api(state["context_b"], state["test_sentence"])
    cleaned = clean_json_response(response)
    score = score_response(cleaned)
    
    state["result_b"] = {
        "raw_response": response,
        "cleaned_response": cleaned,
        "score": score
    }
    state["scores"]["Context B"] = score
    state["current_step"] = "completed_b"
    
    print(f"   Score: {score:.1%}")
    
    return state


def run_context_c(state: ContextEngineringState) -> ContextEngineringState:
    """
    Node C: 測試 Few-shot Context
    """
    print(f"\n🟡 Testing Context C (Few-shot) for test #{state['test_id']}...")
    
    response = call_openai_api(state["context_c"], state["test_sentence"])
    cleaned = clean_json_response(response)
    score = score_response(cleaned)
    
    state["result_c"] = {
        "raw_response": response,
        "cleaned_response": cleaned,
        "score": score
    }
    state["scores"]["Context C"] = score
    state["current_step"] = "completed_c"
    
    print(f"   Score: {score:.1%}")
    
    return state


# ============================================================================
# 5. 建立 LangGraph StateGraph
# ============================================================================

def create_context_engineering_graph():
    """
    建立 Context Engineering 的 StateGraph
    
    流程：Start → A → B → C → End
    """
    # 創建 StateGraph
    workflow = StateGraph(ContextEngineringState)
    
    # 添加節點
    workflow.add_node("context_a", run_context_a)
    workflow.add_node("context_b", run_context_b)
    workflow.add_node("context_c", run_context_c)
    
    # 設置起點
    workflow.set_entry_point("context_a")
    
    # 添加邊：依序執行 A → B → C → END
    workflow.add_edge("context_a", "context_b")
    workflow.add_edge("context_b", "context_c")
    workflow.add_edge("context_c", END)
    
    # 編譯 graph
    app = workflow.compile()
    
    return app


# ============================================================================
# 6. 執行實驗
# ============================================================================

def run_experiment():
    """執行完整的 LangGraph Context Engineering 實驗"""
    
    print("\n" + "="*80)
    print("🎯 LangGraph Context Engineering Experiment")
    print("="*80)
    
    # 測試案例
    test_cases = [
        "這支耳機音質不錯，但藍牙常常斷線。",
        "The keyboard feels great, but the battery dies too fast.",
        "相機畫質很棒，可是夜拍對焦很慢。"
    ]
    
    # 創建 graph
    app = create_context_engineering_graph()
    
    # 儲存所有結果
    all_results = []
    
    # 對每個測試案例執行 graph
    for i, test_sentence in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"📝 Test Case {i}: {test_sentence[:50]}...")
        print(f"{'='*80}")
        
        # 初始化 state
        initial_state: ContextEngineringState = {
            "test_sentence": test_sentence,
            "test_id": i,
            "context_a": CTX_A,
            "context_b": CTX_B,
            "context_c": CTX_C,
            "result_a": {},
            "result_b": {},
            "result_c": {},
            "scores": {},
            "current_step": "start"
        }
        
        # 執行 graph
        final_state = app.invoke(initial_state)
        
        # 儲存結果
        all_results.append({
            "test_id": i,
            "test_sentence": test_sentence,
            "results": {
                "Context A (Baseline)": final_state["result_a"],
                "Context B (Rules-based)": final_state["result_b"],
                "Context C (Few-shot)": final_state["result_c"]
            },
            "scores": final_state["scores"]
        })
        
        # 顯示此測試的總結
        print(f"\n📊 Summary for Test {i}:")
        for ctx_name, score in final_state["scores"].items():
            print(f"   {ctx_name}: {score:.1%}")
    
    # ========================================================================
    # 7. 生成最終報告
    # ========================================================================
    
    print("\n" + "="*80)
    print("📈 FINAL RESULTS")
    print("="*80)
    
    # 計算平均分數
    avg_scores = {
        "Context A (Baseline)": 0.0,
        "Context B (Rules-based)": 0.0,
        "Context C (Few-shot)": 0.0
    }
    
    for result in all_results:
        for ctx_name in avg_scores.keys():
            avg_scores[ctx_name] += result["scores"].get(ctx_name, 0)
    
    for ctx_name in avg_scores.keys():
        avg_scores[ctx_name] /= len(all_results)
    
    # 顯示結果
    print("\n🎯 Average Scores:")
    for ctx_name, avg_score in avg_scores.items():
        bar_length = int(avg_score * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"   {ctx_name:30s} {bar} {avg_score:.1%}")
    
    # 保存到 JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"langgraph_experiment_{timestamp}.json"
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "test_cases": test_cases,
        "results": all_results,
        "average_scores": avg_scores,
        "graph_structure": {
            "nodes": ["context_a", "context_b", "context_c"],
            "edges": [
                ("START", "context_a"),
                ("context_a", "context_b"),
                ("context_b", "context_c"),
                ("context_c", "END")
            ]
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {filename}")
    
    return all_results, avg_scores


# ============================================================================
# 8. 可選：可視化 Graph 結構
# ============================================================================

def visualize_graph():
    """
    可視化 LangGraph 的結構（需要安裝 graphviz）
    """
    try:
        from IPython.display import Image, display
        
        app = create_context_engineering_graph()
        
        # 生成圖片
        graph_image = app.get_graph().draw_mermaid_png()
        
        # 保存
        with open("langgraph_structure.png", "wb") as f:
            f.write(graph_image)
        
        print("✅ Graph visualization saved to: langgraph_structure.png")
        
    except Exception as e:
        print(f"⚠️  Graph visualization not available: {e}")
        print("   Install graphviz and pygraphviz to enable visualization")


# ============================================================================
# 9. Main
# ============================================================================

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  LangGraph Context Engineering Experiment               ║")
    print("║  Using StateGraph to orchestrate A/B/C testing          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # 檢查 API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not set")
        print("Please set it in .env file or environment variable")
    else:
        # 執行實驗
        results, avg_scores = run_experiment()
        
        # 可選：視覺化 graph（需要額外依賴）
        # visualize_graph()
        
        print("\n" + "="*80)
        print("🎉 Experiment completed!")
        print("="*80)
        
        # 顯示最佳策略
        best_strategy = max(avg_scores.items(), key=lambda x: x[1])
        print(f"\n🏆 Best Strategy: {best_strategy[0]} ({best_strategy[1]:.1%})")
