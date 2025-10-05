"""
MCP-Enhanced Context Engineering Experiment (Demo)
====================================================
展示如何使用 MCP 工具動態管理 context 和累積知識

注意：這是一個概念演示，實際 MCP 整合需要 Warp/Claude Desktop 環境
"""

import json
import os
from datetime import datetime
from openai import OpenAI

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
    exit(1)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# MCP 模擬層 (Mock MCP Client)
# ============================================================================

class MockMCPClient:
    """
    模擬 MCP 客戶端，展示如何使用 MCP 工具
    在真實環境中，這會是實際的 MCP 協議呼叫
    """
    
    def __init__(self, memory_dir="./mcp_memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
    
    def call_tool(self, tool_name, params):
        """模擬 MCP 工具呼叫"""
        
        if tool_name == "read_memory":
            return self._read_memory(params["memory_file_name"])
        
        elif tool_name == "write_memory":
            return self._write_memory(
                params["memory_name"], 
                params["content"]
            )
        
        elif tool_name == "list_memories":
            return self._list_memories()
        
        elif tool_name == "search_for_pattern":
            return self._search_pattern(params)
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _read_memory(self, memory_name):
        """讀取專案記憶"""
        file_path = os.path.join(self.memory_dir, f"{memory_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "Memory not found", "exists": False}
    
    def _write_memory(self, memory_name, content):
        """寫入專案記憶"""
        file_path = os.path.join(self.memory_dir, f"{memory_name}.json")
        
        # 如果 content 是字串，嘗試解析為 JSON
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                content = {"raw_content": content}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "path": file_path}
    
    def _list_memories(self):
        """列出所有記憶"""
        memories = []
        for file in os.listdir(self.memory_dir):
            if file.endswith('.json'):
                memories.append(file[:-5])  # Remove .json
        return {"memories": memories}
    
    def _search_pattern(self, params):
        """搜尋模式（簡化版）"""
        # 在真實環境中會搜尋專案文件
        return {
            "matches": [],
            "note": "In real MCP, this would search project files"
        }

# ============================================================================
# MCP 增強的 Context Engineering 實驗
# ============================================================================

mcp = MockMCPClient()

# 測試句子 - 5 個更長、更真實的產品評論
TESTS = [
    "我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，需要重新配對才能使用，這點真的很困擾。",
    
    "The mechanical keyboard I purchased has excellent build quality with a satisfying tactile feedback that makes typing a pleasure. However, I'm quite disappointed with the battery life - it only lasts about 3-4 days with the RGB lighting on, which is far shorter than the advertised 2 weeks. I find myself charging it constantly.",
    
    "這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。",
    
    "I've been using this wireless mouse for gaming and productivity work for the past month. The ergonomic design is comfortable for long sessions, and the precision is excellent for both gaming and design work. The only downside is that the left click button has started developing a double-click issue, which is frustrating during important tasks.",
    
    "這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。"
]

# 基礎 system message
SYS_BASE = "You are a helpful assistant that extracts structured information from text."


def load_best_practices_from_memory():
    """從 MCP memory 載入過往最佳實踐"""
    print("\n📖 Loading best practices from MCP memory...")
    
    result = mcp.call_tool("read_memory", {
        "memory_file_name": "context_best_practices"
    })
    
    if result.get("exists") == False:
        print("   No previous best practices found. Starting fresh.")
        return None
    
    print(f"   ✓ Loaded practices from previous runs")
    print(f"   Last updated: {result.get('updated', 'unknown')}")
    print(f"   Best success rate: {result.get('best_success_rate', 'N/A')}")
    
    return result


def build_dynamic_context(base_rules, previous_practices=None):
    """使用 MCP 記憶動態建構 context"""
    
    context = base_rules
    
    # 如果有過往最佳實踐，整合進來
    if previous_practices:
        context += "\n\n# Learned from previous experiments:"
        
        if "optimal_temperature" in previous_practices:
            context += f"\n- Optimal temperature: {previous_practices['optimal_temperature']}"
        
        if "successful_examples" in previous_practices:
            context += "\n\nProven successful examples:"
            for example in previous_practices['successful_examples'][:2]:
                context += f"\nInput: \"{example['input']}\""
                context += f"\nOutput: {json.dumps(example['output'])}"
    
    return context


def call_model(system_prompt, user_message, model="gpt-4o-mini"):
    """Call OpenAI API"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def clean_json_output(text):
    """Clean JSON from markdown blocks"""
    if "```" in text:
        lines = text.split("\n")
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                json_lines.append(line)
        text = "\n".join(json_lines)
    return text.strip()


def score_json(output_text):
    """Score output"""
    try:
        cleaned = clean_json_output(output_text)
        obj = json.loads(cleaned)
        
        required_keys = {"sentiment", "product", "issue"}
        keys_ok = set(obj.keys()) == required_keys
        
        valid_sentiments = {"positive", "neutral", "negative"}
        sentiment_ok = obj.get("sentiment", "").lower() in valid_sentiments
        
        product_ok = isinstance(obj.get("product"), str) and len(obj.get("product", "")) > 0
        issue_ok = "issue" in obj and isinstance(obj.get("issue"), str)
        
        if keys_ok and sentiment_ok and product_ok and issue_ok:
            return 1, obj, None
        else:
            return 0, obj, "Schema validation failed"
            
    except Exception as e:
        return 0, None, str(e)


def run_mcp_enhanced_experiment():
    """執行 MCP 增強的實驗"""
    
    print("\n" + "="*70)
    print("  MCP-ENHANCED CONTEXT ENGINEERING EXPERIMENT")
    print("  Demonstration: Using MCP for dynamic context management")
    print("="*70)
    
    # 1. 從 MCP memory 載入過往最佳實踐
    previous_practices = load_best_practices_from_memory()
    
    # 2. 定義基礎 context（可以從 MCP 動態載入）
    base_context = """Task: Extract fields from the sentence.
Return ONLY a JSON object with these exact keys: sentiment, product, issue.

Rules:
- sentiment must be one of: positive, neutral, negative
- If product is not explicit, infer the most likely product noun
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text
- Use lowercase English for all field values"""
    
    # 3. 使用 MCP 記憶建構動態 context
    print("\n🔧 Building dynamic context from MCP memory...")
    dynamic_context = build_dynamic_context(base_context, previous_practices)
    
    print(f"   Context length: {len(dynamic_context)} chars")
    if previous_practices:
        print(f"   Integrated {len(previous_practices.get('successful_examples', []))} learned examples")
    
    # 4. 執行實驗
    print("\n" + "="*70)
    print("  RUNNING EXPERIMENTS")
    print("="*70)
    
    results = []
    total_score = 0
    successful_examples = []
    
    for i, test_sentence in enumerate(TESTS, 1):
        print(f"\nTest {i}: {test_sentence}")
        
        full_prompt = f"{dynamic_context}\n\nSentence: {test_sentence}"
        output = call_model(SYS_BASE, full_prompt)
        score, parsed, error = score_json(output)
        
        print(f"Output: {output}")
        print(f"Score: {score}/1 {'✓' if score else f'✗ ({error})'}")
        
        total_score += score
        
        result = {
            "test_id": i,
            "input": test_sentence,
            "output": output,
            "parsed": parsed,
            "score": score
        }
        results.append(result)
        
        # 收集成功案例
        if score == 1:
            successful_examples.append({
                "input": test_sentence,
                "output": parsed
            })
    
    success_rate = total_score / len(TESTS)
    
    # 5. 顯示結果
    print("\n" + "="*70)
    print("  RESULTS")
    print("="*70)
    print(f"\nSuccess Rate: {success_rate*100:.1f}% ({total_score}/{len(TESTS)})")
    
    # 6. 使用 MCP 儲存新的最佳實踐
    print("\n💾 Saving results to MCP memory...")
    
    # 如果這次表現更好，或沒有過往記錄，更新最佳實踐
    should_update = (
        previous_practices is None or 
        success_rate >= previous_practices.get("best_success_rate", 0)
    )
    
    if should_update:
        new_practices = {
            "updated": datetime.now().isoformat(),
            "best_success_rate": success_rate,
            "optimal_temperature": 0.3,
            "successful_examples": successful_examples,
            "context_used": dynamic_context[:200] + "...",  # 儲存部分 context
            "total_runs": previous_practices.get("total_runs", 0) + 1 if previous_practices else 1
        }
        
        result = mcp.call_tool("write_memory", {
            "memory_name": "context_best_practices",
            "content": new_practices
        })
        
        print(f"   ✓ Updated best practices")
        print(f"   Path: {result.get('path')}")
        print(f"   This is run #{new_practices['total_runs']}")
    else:
        print(f"   Previous best ({previous_practices['best_success_rate']*100:.0f}%) was better. Not updating.")
    
    # 7. 儲存詳細結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detailed_results = {
        "timestamp": timestamp,
        "success_rate": success_rate,
        "test_cases": TESTS,
        "results": results,
        "context_used": dynamic_context
    }
    
    mcp.call_tool("write_memory", {
        "memory_name": f"experiment_run_{timestamp}",
        "content": detailed_results
    })
    
    # 8. 顯示 MCP memory 狀態
    print("\n📚 MCP Memory Status:")
    memories = mcp.call_tool("list_memories", {})
    print(f"   Total memories stored: {len(memories['memories'])}")
    for mem in memories['memories']:
        print(f"   - {mem}")
    
    print("\n" + "="*70)
    print("  MCP DEMO COMPLETE")
    print("="*70)
    print("\n💡 Key Takeaways:")
    print("   1. MCP enables persistent learning across runs")
    print("   2. Each experiment builds on previous successes")
    print("   3. Context automatically improves over time")
    print("   4. No manual prompt engineering needed!")
    
    return results


if __name__ == "__main__":
    try:
        run_mcp_enhanced_experiment()
        
        print("\n" + "-"*70)
        print("🚀 Next Steps:")
        print("-"*70)
        print("1. Run this script multiple times to see learning in action")
        print("2. Check ./mcp_memory/ folder to see stored knowledge")
        print("3. Modify test cases and watch context adapt")
        print("4. In real Warp/Claude Desktop, MCP tools are automatically available")
        
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
