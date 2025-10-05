# Context 可視化調試工具使用指南 🎨

## 概述

這套工具讓您能夠**可視化不同 context 策略的演變過程**，就像使用 `git diff` 查看代碼變更一樣，但追蹤的是 **AI 的上下文如何變化**。

## 🎯 這個工具解決了什麼問題？

回答您的問題：
> "使用自製 DIFF 工具或 Chainlit、Serena MCP 等，做 context 注入/演變效果的可視化調試，便於比較不同 context 設計的實際回應差異。"

這個工具提供：

1. **Context DIFF** - 像 git diff 一樣比較不同 context 版本
2. **Token 追蹤** - 監控每個 context 的 token 使用量變化
3. **回應質量對比** - 並排比較不同 context 產生的實際輸出
4. **演變時間軸** - 追蹤 context 的逐步改進過程
5. **互動式調試** - 快速識別哪些 context 改動帶來了改進

## 📁 文件說明

### 1. `context_visualizer.py` - 核心可視化引擎

**功能：**
- Context 快照管理
- DIFF 生成與顯示
- Token 計數
- 相似度分析
- 並排比較
- 結果導出

**使用範例：**
```python
from context_visualizer import ContextVisualizer

viz = ContextVisualizer()

# 添加不同版本的 context
viz.add_snapshot("Version 1", "Your context here...")
viz.add_snapshot("Version 2", "Improved context...")

# 查看差異
viz.show_diff(0, 1)

# 查看演變
viz.show_evolution()

# 導出結果
viz.export_comparison()
```

### 2. `context_visualizer_live.py` - 整合真實 API

**功能：**
- 真實調用 OpenAI API
- 自動測試三種 context 策略
- 實時顯示結果
- 自動評分
- 完整的實驗流程

**運行：**
```bash
python context_visualizer_live.py
```

**輸出示例：**
```
╔══════════════════════════════════════════════════════════╗
║  Live Context Engineering Visualizer                    ║
║  Real-time API calls + Visualization                    ║
╚══════════════════════════════════════════════════════════╝

📸 Capturing context snapshots...

✅ Added snapshot: Context A (Baseline) | 15 tokens | 87 chars
✅ Added snapshot: Context B (Rules-based) | 63 tokens | 401 chars
✅ Added snapshot: Context C (Few-shot) | 125 tokens | 812 chars

📈 Context Evolution Timeline

┌────────┬──────────────────────┬────────┬──────────┬──────────┐
│ Step   │ Context Name         │ Tokens │ Δ Tokens │ Time     │
├────────┼──────────────────────┼────────┼──────────┼──────────┤
│ #0     │ Context A (Baseline) │     15 │          │ 14:23:45 │
│ #1     │ Context B (Rules)    │     63 │      +48 │ 14:23:45 │
│ #2     │ Context C (Few-shot) │    125 │      +62 │ 14:23:46 │
└────────┴──────────────────────┴────────┴──────────┴──────────┘

================================================================================

📊 Comparing:
  A: Context A (Baseline) | 15 tokens | 87 chars
  B: Context B (Rules-based) | 63 tokens | 401 chars
  Token Δ: +48

╭──────────────────────── Context Diff ────────────────────────╮
│   1 --- Context A (Baseline)                                 │
│   2 +++ Context B (Rules-based)                              │
│   3  You are a sentiment analyzer.                           │
│   4 -Extract product info from this review.                  │
│   5 +                                                         │
│   6 +Extract the following information from product reviews: │
│   7 +- sentiment: must be "positive", "neutral", or "negative"│
│   8 +- product: the product name (string)                    │
│   9 +- issue: description of any issues (string, or empty)   │
│  10 +                                                         │
│  11 +Output must be valid JSON format.                       │
│  12 +Do not include markdown code blocks.                    │
╰──────────────────────────────────────────────────────────────╯
```

## 🔍 主要視覺化功能

### 1. Context Evolution Timeline（演變時間軸）

顯示每個 context 版本的：
- Token 數量
- 相對於前一版本的增減
- 時間戳記

```python
viz.show_evolution()
```

### 2. Context Diff（差異比較）

像 `git diff` 一樣顯示：
- ➕ 新增的內容（綠色）
- ➖ 刪除的內容（紅色）
- 行號標記

```python
viz.show_diff(0, 1)  # 比較版本 0 和版本 1
```

### 3. Side-by-Side Comparison（並排比較）

並排顯示兩個 context，方便直觀比較：

```
┌─────────────────────────────┬─────────────────────────────┐
│ Context A (Baseline)        │ Context C (Few-shot)        │
│ 15 tokens                   │ 125 tokens                  │
│─────────────────────────────│─────────────────────────────│
│ You are a sentiment...      │ You are a sentiment...      │
│ Extract product info...     │                             │
│                             │ Extract the following...    │
│                             │ - sentiment: must be...     │
│                             │                             │
│                             │ Examples:                   │
│                             │ Input: "這支耳機..."        │
│                             │ Output: {"sentiment": ...}  │
└─────────────────────────────┴─────────────────────────────┘
```

```python
viz.show_side_by_side(0, 2)
```

### 4. Similarity Analysis（相似度分析）

計算兩個 context 的相似度百分比：

```
Similarity Score: 45.2%
████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 45.2%
```

```python
viz.show_similarity(0, 2)
```

### 5. Response Comparison（回應比較）

比較不同 context 產生的實際輸出：

```
🎯 Response Comparison

┌──────────────────────┬──────┬────────┬─────────────────────────┐
│ Context              │ Score│ Length │ Preview                 │
├──────────────────────┼──────┼────────┼─────────────────────────┤
│ Context A (Baseline) │ 50%  │    47  │ {"sentiment": "positive"│
│ Context B (Rules)    │ 80%  │    79  │ {"sentiment": "negative"│
│ Context C (Few-shot) │ 100% │   102  │ {"sentiment": "negative"│
└──────────────────────┴──────┴────────┴─────────────────────────┘
```

```python
viz.show_response_comparison()
```

## 🚀 快速開始

### 安裝依賴

```bash
pip install rich tiktoken openai python-dotenv
```

### 1. 運行演示版本（不需要 API）

```bash
python context_visualizer.py
```

這會展示所有可視化功能，使用模擬數據。

### 2. 運行真實 API 版本

```bash
# 確保已設置 API key
python context_visualizer_live.py
```

這會：
1. 捕捉三種 context 快照
2. 真實調用 OpenAI API
3. 顯示完整的 diff 和演變過程
4. 比較實際回應質量
5. 導出詳細結果

## 📊 輸出文件

### 1. `context_comparison_TIMESTAMP.json`

包含所有 context 快照和回應：

```json
{
  "snapshots": [
    {
      "name": "Context A (Baseline)",
      "content": "...",
      "tokens": 15,
      "timestamp": "2025-10-05T14:23:45",
      "metadata": {"strategy": "baseline"}
    }
  ],
  "responses": {
    "Context A (Baseline)": {
      "content": "{...}",
      "score": 0.5,
      "length": 47
    }
  }
}
```

### 2. `live_experiment_TIMESTAMP.json`

包含完整的實驗結果：

```json
{
  "timestamp": "2025-10-05T14:23:45",
  "tests": ["測試案例 1", "測試案例 2", ...],
  "results": {
    "Context A (Baseline)": {
      "scores": [0.5, 0.75, 0.5],
      "avg_score": 0.58,
      "responses": ["...", "...", "..."]
    }
  }
}
```

## 🎓 實際應用場景

### 場景 1：改進 Prompt 設計

```python
viz = ContextVisualizer()

# 第一版
viz.add_snapshot("V1", "Extract product info")

# 第二版：加入規則
viz.add_snapshot("V2", "Extract product info\nRules: ...")

# 第三版：加入範例
viz.add_snapshot("V3", "Extract product info\nRules: ...\nExamples: ...")

# 查看每次改進的影響
viz.show_evolution()
viz.show_diff(0, 1)
viz.show_diff(1, 2)
```

### 場景 2：A/B 測試不同策略

```python
strategies = {
    "Short & Sweet": "Brief instruction",
    "Detailed Rules": "Long detailed rules...",
    "Few-shot Learning": "Rules + examples...",
}

viz = ContextVisualizer()

for name, content in strategies.items():
    viz.add_snapshot(name, content)
    
    # 調用 API 測試
    response = call_api(content)
    score = evaluate(response)
    
    viz.add_response(name, response, score)

# 比較所有策略
viz.show_response_comparison()
```

### 場景 3：Debug 失敗的 Prompt

```python
# 失敗的版本
viz.add_snapshot("Failing V1", failing_prompt)

# 嘗試修復
viz.add_snapshot("Fix Attempt 1", fixed_v1)
viz.add_snapshot("Fix Attempt 2", fixed_v2)

# 找出哪些改動有效
viz.show_diff(0, 1)  # V1 vs Fix 1
viz.show_diff(1, 2)  # Fix 1 vs Fix 2

# 測試每個版本
for i, name in enumerate(["Failing V1", "Fix Attempt 1", "Fix Attempt 2"]):
    response = test_prompt(viz.snapshots[i].content)
    viz.add_response(name, response, score_it(response))

viz.show_response_comparison()
```

## 🔗 與 MCP 整合

這個工具可以與 MCP (Model Context Protocol) 整合：

```python
from context_visualizer import ContextVisualizer

viz = ContextVisualizer()

# 從 MCP memory 讀取過往最佳 context
best_context = mcp_client.call_tool("read_memory", {
    "memory_file_name": "best_context"
})

viz.add_snapshot("Previous Best", best_context)

# 嘗試新的改進
new_context = improve_context(best_context)
viz.add_snapshot("New Attempt", new_context)

# 比較差異
viz.show_diff(0, 1)

# 如果新版本更好，保存到 MCP memory
if test_score > previous_best:
    mcp_client.call_tool("write_memory", {
        "memory_name": "best_context",
        "content": new_context
    })
```

## 💡 進階用法

### 自定義評分函數

```python
def custom_scorer(response: str) -> float:
    """自定義評分邏輯"""
    score = 0.0
    
    # 檢查 JSON 格式
    try:
        data = json.loads(response)
        score += 0.3
    except:
        return 0.0
    
    # 檢查必要欄位
    required_fields = ["sentiment", "product", "issue"]
    for field in required_fields:
        if field in data:
            score += 0.2
    
    # 檢查語意正確性
    if is_semantically_correct(data):
        score += 0.3
    
    return min(score, 1.0)
```

### 批量比較多個策略

```python
strategies = load_all_strategies()
viz = ContextVisualizer()

for name, context in strategies.items():
    viz.add_snapshot(name, context)

# 生成比較矩陣
for i in range(len(strategies)):
    for j in range(i + 1, len(strategies)):
        print(f"\nComparing {i} vs {j}:")
        viz.show_diff(i, j)
        viz.show_similarity(i, j)
```

## 🎯 與其他工具的對比

| 工具 | 用途 | 優勢 |
|------|------|------|
| **這個工具** | Context 可視化調試 | 專注於 context diff，輕量級 |
| **Chainlit** | 對話 UI 框架 | 完整的對話介面，適合生產環境 |
| **Langfuse** | AI 可觀測性平台 | 企業級追蹤，多專案管理 |
| **Serena MCP** | MCP 調試 | 專注於 MCP 協議調試 |

## 📚 延伸閱讀

- [原始實驗](./README.md) - Context Engineering Lab 基礎實驗
- [MCP 整合](./MCP_CONTEXT_ENGINEERING.md) - 如何與 MCP 結合
- [Few-shot 比較](./FEWSHOT_COMPARISON.md) - Few-shot learning 深入分析

## 🐛 故障排除

### Token 計數不準確

如果沒有安裝 `tiktoken`，會使用簡單的字數統計作為替代。安裝正確版本：

```bash
pip install tiktoken
```

### Rich 顯示問題

如果終端不支持 Rich 的顏色輸出：

```python
from rich.console import Console
console = Console(force_terminal=False)
```

### API 錯誤

確保 `.env` 文件包含有效的 API key：

```
OPENAI_API_KEY=sk-...
```

## 🎉 總結

這個工具回答了您的問題：**如何可視化 context 注入/演變效果**。

關鍵特點：
- ✅ 像 git diff 一樣的 context 比較
- ✅ Token 使用追蹤
- ✅ 並排視覺化
- ✅ 實際回應質量對比
- ✅ 完整的演變時間軸
- ✅ 可導出的結果報告

立即開始使用：

```bash
# 演示版
python context_visualizer.py

# 真實 API 版
python context_visualizer_live.py
```

---

**Happy Context Engineering! 🚀**
