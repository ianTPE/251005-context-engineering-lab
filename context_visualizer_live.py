"""
Live Context Visualizer with Real API
整合真實 OpenAI API 的 Context 可視化工具

這個工具會：
1. 真實調用 OpenAI API
2. 追蹤每次 context 變化
3. 即時顯示 diff 和演變
4. 比較不同策略的實際效果
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from context_visualizer import ContextVisualizer

# 載入環境變數
load_dotenv()

# 初始化 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 測試案例
TESTS = [
    "這支耳機音質不錯，但藍牙常常斷線。",
    "The keyboard feels great, but the battery dies too fast.",
    "相機畫質很棒，可是夜拍對焦很慢。"
]


def call_model(system_prompt, user_message, model="gpt-4o-mini"):
    """調用 OpenAI API"""
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


def score_response(response: str) -> float:
    """簡單的評分函數"""
    score = 0.0
    
    # 檢查是否為有效 JSON
    try:
        data = json.loads(response)
        score += 0.25
        
        # 檢查必要欄位
        if "sentiment" in data:
            score += 0.25
        if "product" in data:
            score += 0.25
        if "issue" in data:
            score += 0.25
        
        # 檢查 sentiment 值是否合法
        if data.get("sentiment") in ["positive", "neutral", "negative"]:
            score += 0.25
        
        # 額外分：product 非空
        if data.get("product") and data.get("product").strip():
            score += 0.25
        
    except:
        pass
    
    return min(score, 1.0)


def run_live_experiment():
    """執行真實的 API 實驗並可視化"""
    
    # 初始化可視化器
    viz = ContextVisualizer()
    
    # 定義三種 Context
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
    
    # 添加 snapshots
    print("\n📸 Capturing context snapshots...\n")
    viz.add_snapshot("Context A (Baseline)", CTX_A, {"strategy": "baseline"})
    viz.add_snapshot("Context B (Rules-based)", CTX_B, {"strategy": "rules"})
    viz.add_snapshot("Context C (Few-shot)", CTX_C, {"strategy": "fewshot"})
    
    # 顯示演變
    viz.show_evolution()
    
    # 顯示 Context A vs B 差異
    print("\n" + "="*80)
    viz.show_diff(0, 1)
    
    # 顯示 Context B vs C 差異
    print("\n" + "="*80)
    viz.show_diff(1, 2)
    
    # 測試每個 context
    contexts = [
        ("Context A (Baseline)", CTX_A),
        ("Context B (Rules-based)", CTX_B),
        ("Context C (Few-shot)", CTX_C)
    ]
    
    print("\n" + "="*80)
    print("\n🧪 Running live experiments with OpenAI API...\n")
    
    results = {}
    
    for ctx_name, ctx_content in contexts:
        print(f"\n Testing {ctx_name}...")
        
        scores = []
        responses_text = []
        
        for i, test in enumerate(TESTS, 1):
            print(f"  Test {i}/3...", end=" ")
            
            # 調用 API
            response = call_model(ctx_content, test)
            
            # 清理 markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
                if response.startswith("json"):
                    response = response[4:].strip()
            
            # 評分
            test_score = score_response(response)
            scores.append(test_score)
            responses_text.append(response)
            
            print(f"Score: {test_score:.1%}")
        
        # 計算平均分
        avg_score = sum(scores) / len(scores)
        results[ctx_name] = {
            "scores": scores,
            "avg_score": avg_score,
            "responses": responses_text
        }
        
        # 記錄到可視化器（使用第一個回應作為代表）
        viz.add_response(ctx_name, responses_text[0], avg_score)
        
        print(f"  ✅ Average Score: {avg_score:.1%}")
    
    # 顯示並排比較
    print("\n" + "="*80)
    viz.show_side_by_side(0, 2, max_lines=15)
    
    # 顯示相似度
    print("\n" + "="*80)
    print("\n[Similarity Analysis]")
    viz.show_similarity(0, 2)
    
    # 顯示回應比較
    viz.show_response_comparison()
    
    # 詳細結果表格
    print("\n" + "="*80)
    print("\n📊 Detailed Results:\n")
    
    for ctx_name, result in results.items():
        print(f"{ctx_name}:")
        for i, (test, score) in enumerate(zip(TESTS, result["scores"]), 1):
            print(f"  Test {i}: {score:.1%} | {test[:40]}...")
        print(f"  Average: {result['avg_score']:.1%}\n")
    
    # 導出
    viz.export_comparison()
    
    # 保存詳細結果
    detailed_filename = f"live_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(detailed_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": TESTS,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detailed results saved to {detailed_filename}")
    
    return results


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  Live Context Engineering Visualizer                    ║")
    print("║  Real-time API calls + Visualization                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # 檢查 API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not set")
        print("Please set it in .env file or environment variable")
    else:
        results = run_live_experiment()
        
        print("\n" + "="*80)
        print("\n🎉 Experiment completed! Check the exported files for details.")
