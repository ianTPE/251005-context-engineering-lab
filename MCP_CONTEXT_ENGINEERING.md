# MCP 在 Context Engineering 中的角色

## 🎯 什麼是 MCP？

**MCP (Model Context Protocol)** 是一個標準化協議，讓 AI 模型能夠：
- 從外部工具動態獲取資訊
- 連接到個人化數據源
- 即時取得最新上下文
- 整合各種 API 和服務

## 🔗 MCP 與 Context Engineering 的關係

### 傳統 Context Engineering
```
靜態提示詞 (Prompt) → 模型 → 輸出
```

### MCP 增強的 Context Engineering
```
靜態提示詞 + MCP動態上下文 → 模型 → 輸出
              ↑
          (即時獲取)
    - 檔案內容
    - 程式碼結構
    - 專案記憶
    - 搜尋結果
    - API 回應
```

## 📊 在我們實驗中的潛在應用

### 1. **動態測試案例生成**

**不使用 MCP (當前版本)**：
```python
TESTS = [
    "這支耳機音質不錯，但藍牙常常斷線。",
    "The keyboard feels great...",
    "相機畫質很棒..."
]
```

**使用 MCP 增強**：
```python
# 從真實產品評論資料庫動態載入
from mcp import search_reviews

TESTS = mcp_client.call_tool(
    "search_reviews",
    {
        "source": "amazon_reviews",
        "categories": ["electronics"],
        "sample_size": 10,
        "languages": ["zh", "en"]
    }
)
```

### 2. **上下文記憶管理**

**使用 MCP 的 Memory 工具**：
```python
# 儲存實驗結果到專案記憶
mcp_client.call_tool("write_memory", {
    "memory_name": "context_experiment_best_practices",
    "content": """
    實驗發現：
    - Context C (Few-shot) 達成 100% 成功率
    - 關鍵因素：2個具體範例 + 嚴格規則
    - 最佳溫度設定：0.3
    """
})

# 下次實驗時自動讀取
previous_findings = mcp_client.call_tool(
    "read_memory",
    {"memory_file_name": "context_experiment_best_practices"}
)
```

### 3. **程式碼符號分析**

**使用 MCP 的 Symbol 工具**：
```python
# 找出專案中所有的 context 定義
contexts = mcp_client.call_tool("find_symbol", {
    "name_path": "CTX_",
    "substring_matching": True,
    "relative_path": "."
})

# 分析每個 context 的使用頻率
for ctx in contexts:
    references = mcp_client.call_tool(
        "find_referencing_symbols",
        {
            "name_path": ctx["name"],
            "relative_path": ctx["file"]
        }
    )
```

### 4. **專案感知的 Context 優化**

**使用 MCP 的 Project 工具**：
```python
# 載入專案結構
project_structure = mcp_client.call_tool("list_dir", {
    "relative_path": ".",
    "recursive": True
})

# 根據專案特性調整 context
if "tests/" in project_structure:
    # 為測試專案使用更嚴格的 schema
    CTX_B += "\n- Must include test_id field"
```

## 🌟 實際範例：MCP 增強的 Context 實驗

讓我們建立一個使用 MCP 的進階版本：

```python
"""
MCP-Enhanced Context Engineering Experiment
使用 MCP 動態載入上下文和記憶
"""

from openai import OpenAI
from mcp_client import MCPClient  # 假設的 MCP 客戶端

client = OpenAI()
mcp = MCPClient()

# 1. 從專案記憶中讀取過往最佳實踐
previous_best = mcp.call_tool("read_memory", {
    "memory_file_name": "context_best_practices"
})

# 2. 動態建構 Context C，包含過往成功案例
CTX_C = f"""
{previous_best.get('rules', '')}

Examples (from previous successful runs):
{previous_best.get('examples', '')}

New example:
Input: "這支耳機音質不錯，但藍牙常常斷線。"
Output: {{"sentiment": "negative", "product": "headphones", "issue": "bluetooth"}}
"""

# 3. 從真實數據源動態載入測試案例
TESTS = mcp.call_tool("search_for_pattern", {
    "substring_pattern": "product review",
    "relative_path": "./data/reviews",
    "context_lines_after": 2
})

# 4. 執行實驗
results = run_experiment(CTX_C, TESTS)

# 5. 儲存新的最佳實踐到記憶
if results['success_rate'] > 0.95:
    mcp.call_tool("write_memory", {
        "memory_name": "context_best_practices",
        "content": f"""
        Updated: {datetime.now()}
        Success Rate: {results['success_rate']}
        Best Context: {CTX_C}
        """
    })
```

## 🎓 MCP 在 Context Engineering 的三大優勢

### 1. **動態性 (Dynamic)**
- 不需要硬編碼所有測試案例
- 可以從真實數據源即時抓取
- 根據環境自動調整

### 2. **記憶性 (Memory)**
- 累積過往實驗的最佳實踐
- 避免重複低效的 context 設計
- 建立專案特定的 prompt library

### 3. **感知性 (Awareness)**
- 理解專案結構
- 知道哪些檔案存在
- 能夠分析程式碼符號
- 追蹤依賴關係

## 🔧 可用的 MCP 工具（在 Context Engineering 中）

根據你環境中提供的 MCP 工具：

| MCP 工具 | Context Engineering 用途 |
|---------|------------------------|
| `find_symbol` | 找出專案中的 context 定義 |
| `search_for_pattern` | 搜尋測試案例或範例 |
| `read_memory` | 讀取過往最佳 context |
| `write_memory` | 儲存成功的 context 模式 |
| `list_dir` | 分析專案結構以調整 context |
| `get_symbols_overview` | 理解程式碼結構 |
| `find_referencing_symbols` | 追蹤 context 使用情況 |

## 💡 實際應用場景

### 場景 1：多專案 Context 管理
```python
# 為不同專案維護不同的 context 策略
project_name = mcp.call_tool("activate_project", {
    "project": "ecommerce-sentiment-analysis"
})

# 載入該專案的最佳 context
project_context = mcp.call_tool("read_memory", {
    "memory_file_name": f"{project_name}_context_rules"
})
```

### 場景 2：自動 Few-shot 範例生成
```python
# 從過往成功案例中自動選擇最佳範例
successful_cases = mcp.call_tool("search_for_pattern", {
    "substring_pattern": '"score": 1',
    "relative_path": "./results",
    "context_lines_before": 3
})

# 使用這些案例建構 few-shot context
CTX_C = build_fewshot_context(successful_cases[:5])
```

### 場景 3：A/B 測試歷史追蹤
```python
# 記錄每次實驗結果
mcp.call_tool("write_memory", {
    "memory_name": f"experiment_{timestamp}",
    "content": json.dumps({
        "contexts": [CTX_A, CTX_B, CTX_C],
        "results": results,
        "winner": "Context C"
    })
})

# 分析歷史趨勢
all_experiments = mcp.call_tool("list_memories", {})
analyze_trends(all_experiments)
```

## 🚀 將 MCP 整合到當前實驗

想要試試看嗎？我可以建立一個 MCP 增強版本：

```python
# context_experiment_mcp.py
# 使用 MCP 動態管理 context 和測試案例
```

優點：
- ✅ 自動從過往實驗學習
- ✅ 動態調整測試案例
- ✅ 累積專案知識
- ✅ 支援多專案管理

## 📊 對比總結

| 特性 | 靜態 Context | MCP 增強 Context |
|-----|------------|-----------------|
| 測試案例 | 硬編碼 | 動態載入 |
| 最佳實踐 | 手動更新 | 自動記憶 |
| 專案感知 | 無 | 完整結構感知 |
| 可擴展性 | 低 | 高 |
| 學習能力 | 無 | 持續改進 |

## 🎯 下一步建議

1. **基礎實驗**（當前）：
   - 先完成靜態 context 實驗
   - 理解三種 context 策略差異
   
2. **MCP 增強**（進階）：
   - 整合 memory 工具
   - 建立 context 知識庫
   - 實現自動優化循環

3. **生產級**（專家）：
   - 多專案 context 管理
   - A/B 測試自動化
   - Context 性能監控

---

**總結**：MCP 讓 Context Engineering 從「靜態設計」進化到「動態自適應系統」，是構建可持續改進的 AI 系統的關鍵技術。
