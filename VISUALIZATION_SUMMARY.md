# 🎨 Context 可視化工具 - 完整說明

## 📌 回答你的問題

### 問題 1: MCP 與 Context Engineering 的關係
> "結合 MCP 類型工具或 AI Observability 工具（如 Langfuse），可以自動捕捉 context 變化軌跡，做更深入 prompt trace 與 context engineering 研究。"

**簡單來說：**
- **MCP (Model Context Protocol)** = 讓 AI 從外部工具動態獲取資訊的協議
- **AI Observability (如 Langfuse)** = 追蹤和分析 AI 行為的平台
- **目的：** 自動記錄 AI 的上下文如何隨時間演變，分析哪些 context 設計最有效

**就像：**
- Git 追蹤代碼變更 → MCP/Langfuse 追蹤 context 變更
- Git diff 顯示代碼差異 → 我們的工具顯示 context 差異
- Git blame 找出誰改了代碼 → Context trace 找出哪個改動影響了 AI 輸出

### 問題 2: Context 可視化調試
> "使用自製 DIFF 工具或 Chainlit、Serena MCP 等，做 context 注入/演變效果的可視化調試，便於比較不同 context 設計的實際回應差異。"

**簡單來說：**
就是建立一個**像 git diff 的工具，但追蹤的是 AI 的 context（上下文）變化**，讓你能：

1. **看到差異** - Context A 和 Context B 有什麼不同？
2. **追蹤演變** - Context 如何從 v1 → v2 → v3 改進？
3. **比較效果** - 不同 context 產生的回應有何差異？
4. **測量影響** - 哪些改動真正提升了 AI 表現？

## 🛠️ 我們建立的工具

### 核心文件

| 文件 | 用途 | 何時使用 |
|------|------|----------|
| `context_visualizer.py` | 核心可視化引擎 | 演示功能（無需 API） |
| `context_visualizer_live.py` | 整合真實 API 的實驗 | 真實測試（需要 API） |
| `QUICKSTART_VISUALIZATION.md` | 5 分鐘快速開始 | 初學者入門 |
| `VISUALIZATION_GUIDE.md` | 完整使用指南 | 深入學習 |

### 關鍵功能

#### 1️⃣ Context Snapshot（快照）
```python
viz = ContextVisualizer()
viz.add_snapshot("Version 1", "Your context here...")
viz.add_snapshot("Version 2", "Improved context...")
```

**作用：** 保存每個版本的 context，就像 git commit

#### 2️⃣ Context Diff（差異比較）
```python
viz.show_diff(0, 1)  # 比較版本 0 和 1
```

**輸出：**
```diff
--- Version 1
+++ Version 2
 You are a sentiment analyzer.
-Extract product info.
+Extract the following:
+- sentiment: positive/neutral/negative
+- product: product name
+- issue: any issues
```

**作用：** 像 git diff 一樣顯示改動

#### 3️⃣ Evolution Timeline（演變時間軸）
```python
viz.show_evolution()
```

**輸出：**
```
📈 Context Evolution Timeline

┌────────┬─────────────┬────────┬──────────┐
│ Step   │ Name        │ Tokens │ Δ Tokens │
├────────┼─────────────┼────────┼──────────┤
│ #0     │ Baseline    │     15 │          │
│ #1     │ + Rules     │     63 │      +48 │
│ #2     │ + Examples  │    125 │      +62 │
└────────┴─────────────┴────────┴──────────┘
```

**作用：** 追蹤 token 使用和改動軌跡

#### 4️⃣ Response Comparison（回應比較）
```python
viz.add_response("Baseline", response1, score=0.5)
viz.add_response("+ Rules", response2, score=0.8)
viz.show_response_comparison()
```

**輸出：**
```
🎯 Response Comparison

┌─────────────┬───────┬─────────────────┐
│ Context     │ Score │ Preview         │
├─────────────┼───────┼─────────────────┤
│ Baseline    │  50%  │ {"product": ""} │
│ + Rules     │  80%  │ {"sentiment":...│
│ + Examples  │ 100%  │ {"sentiment":...│
└─────────────┴───────┴─────────────────┘
```

**作用：** 比較不同 context 的實際效果

#### 5️⃣ Side-by-Side（並排顯示）
```python
viz.show_side_by_side(0, 2)
```

**作用：** 並排顯示兩個 context，直觀比較

#### 6️⃣ Similarity Analysis（相似度分析）
```python
viz.show_similarity(0, 2)
```

**輸出：**
```
Similarity Score: 45.2%
████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 45.2%
```

**作用：** 量化兩個 context 的相似程度

## 🎯 實際應用流程

### 典型工作流程

```
1. 起點：Baseline Context
   ↓
2. 添加快照並測試
   viz.add_snapshot("Baseline", baseline_prompt)
   ↓
3. 嘗試改進版本
   viz.add_snapshot("V2", improved_prompt)
   ↓
4. 查看差異
   viz.show_diff(0, 1)
   ↓
5. 真實測試
   response = call_api(improved_prompt)
   viz.add_response("V2", response, score)
   ↓
6. 比較效果
   viz.show_response_comparison()
   ↓
7. 迭代改進
   重複步驟 3-6
   ↓
8. 導出結果
   viz.export_comparison()
```

### 實例：修復 AI 產品評論分析

**問題：** AI 無法正確提取產品資訊

**步驟 1：確認問題**
```python
viz = ContextVisualizer()

baseline = "Extract product info from this review."
viz.add_snapshot("Baseline", baseline)

# 測試
response = call_api(baseline, "相機畫質很棒，可是夜拍對焦很慢。")
# 結果: {"product": ""}  ❌ 空的！

viz.add_response("Baseline", response, score=0.3)
```

**步驟 2：加入明確規則**
```python
v2 = """Extract the following:
- sentiment: "positive", "neutral", or "negative"
- product: the product name
- issue: any issues (or empty string)

Output valid JSON only."""

viz.add_snapshot("V2: Rules", v2)

# 查看改動
viz.show_diff(0, 1)
```

**輸出：**
```diff
--- Baseline
+++ V2: Rules
-Extract product info from this review.
+Extract the following:
+- sentiment: "positive", "neutral", or "negative"
+- product: the product name
+- issue: any issues (or empty string)
+
+Output valid JSON only.
```

**步驟 3：測試改進效果**
```python
response = call_api(v2, "相機畫質很棒，可是夜拍對焦很慢。")
# 結果: {"sentiment": "negative", "product": "camera", "issue": "slow focus"}
# ✅ 好多了！

viz.add_response("V2: Rules", response, score=0.8)
```

**步驟 4：加入範例（Few-shot）**
```python
v3 = v2 + """

Examples:

Input: "這支耳機音質不錯，但藍牙常常斷線。"
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth"}

Input: "The keyboard feels great, but battery dies fast."
Output: {"sentiment": "negative", "product": "keyboard", "issue": "battery life"}"""

viz.add_snapshot("V3: Few-shot", v3)

# 測試
response = call_api(v3, "相機畫質很棒，可是夜拍對焦很慢。")
# 結果: {"sentiment": "negative", "product": "camera", "issue": "night mode autofocus slow"}
# ✅ 完美！更詳細！

viz.add_response("V3: Few-shot", response, score=1.0)
```

**步驟 5：查看完整演變**
```python
viz.show_evolution()
viz.show_response_comparison()
viz.export_comparison()
```

**結果：**
```
改進軌跡：
Baseline (30% accurate)
    ↓ +48 tokens
V2: Rules (80% accurate)
    ↓ +62 tokens
V3: Few-shot (100% accurate) ✅

結論：加入明確規則和範例，準確度提升 70%
```

## 📊 與其他工具的比較

| 特性 | 我們的工具 | Chainlit | Langfuse | Serena MCP |
|------|-----------|----------|----------|------------|
| **主要用途** | Context diff & 可視化 | 對話 UI 框架 | AI 可觀測平台 | MCP 協議調試 |
| **學習曲線** | ⭐⭐ 簡單 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 複雜 | ⭐⭐⭐ 中等 |
| **安裝複雜度** | `pip install rich` | 需要配置 | 需要帳號 | 需要 MCP 環境 |
| **適用場景** | 快速 prompt 調試 | 生產級對話應用 | 企業級監控 | MCP 開發 |
| **輸出格式** | 終端 + JSON | Web UI | Dashboard | 調試界面 |
| **成本** | 免費 | 免費 | 有免費版 | 免費 |

### 何時使用哪個工具？

**使用我們的工具：**
- ✅ 快速調試 prompt
- ✅ 比較不同策略
- ✅ 學習 context engineering
- ✅ 輕量級實驗

**使用 Chainlit：**
- ✅ 建立對話 UI
- ✅ 生產環境部署
- ✅ 需要完整對話界面

**使用 Langfuse：**
- ✅ 企業級監控
- ✅ 多專案管理
- ✅ 長期追蹤分析

**使用 Serena MCP：**
- ✅ 調試 MCP 協議
- ✅ 開發 MCP 工具
- ✅ 檢查 MCP 交互

## 🔗 與 MCP 整合

我們的工具可以與 MCP 結合：

```python
from context_visualizer import ContextVisualizer

viz = ContextVisualizer()

# 從 MCP memory 讀取過往最佳 context
best_context = mcp_client.call_tool("read_memory", {
    "memory_file_name": "best_context_v1"
})

viz.add_snapshot("Previous Best", best_context)

# 嘗試改進
new_context = improve(best_context)
viz.add_snapshot("New Attempt", new_context)

# 比較
viz.show_diff(0, 1)

# 測試
response = test_with_api(new_context)
score = evaluate(response)
viz.add_response("New Attempt", response, score)

# 如果更好，保存到 MCP
if score > previous_best_score:
    mcp_client.call_tool("write_memory", {
        "memory_name": "best_context_v2",
        "content": new_context
    })
```

## 🚀 快速開始

### 最快 3 步驟

```bash
# 1. 安裝依賴
pip install rich tiktoken openai python-dotenv

# 2. 運行演示（無需 API）
python context_visualizer.py

# 3. 運行真實實驗（需要 API key）
python context_visualizer_live.py
```

### 文檔導航

1. **完全新手？** → 讀 `QUICKSTART_VISUALIZATION.md`
2. **想深入了解？** → 讀 `VISUALIZATION_GUIDE.md`
3. **想了解 MCP？** → 讀 `MCP_CONTEXT_ENGINEERING.md`
4. **想看原始實驗？** → 讀 `README.md`

## 💡 關鍵收穫

### 1. Context 就是"工作指南"
- 好的 context = 明確的指示 + 具體的範例
- 壞的 context = 模糊的描述 + 沒有範例

### 2. 可視化讓改進更容易
- 看到差異 → 理解改動
- 追蹤演變 → 學習模式
- 比較結果 → 證實效果

### 3. 系統化實驗很重要
- 記錄每次嘗試
- 測量實際效果
- 迭代改進策略

## 📈 下一步探索

### 初學者路徑
1. ✅ 運行 `context_visualizer.py` 看演示
2. ✅ 閱讀 `QUICKSTART_VISUALIZATION.md`
3. ✅ 修改測試案例實驗
4. ✅ 運行 `context_visualizer_live.py`

### 進階路徑
1. ✅ 自定義評分函數
2. ✅ 整合到自己的專案
3. ✅ 建立 context 知識庫
4. ✅ 追蹤長期改進趨勢

### 專家路徑
1. ✅ 與 MCP 整合
2. ✅ 建立自動優化循環
3. ✅ 多策略批量測試
4. ✅ 貢獻改進到工具

## 🎉 總結

這套工具解答了你的兩個問題：

1. **MCP & Observability** = 自動追蹤 context 演變軌跡
2. **可視化調試** = 像 git diff 一樣比較 context 差異

**核心價值：**
- 🎯 讓 context engineering 從"靠直覺"變成"有數據"
- 📊 清楚看到什麼改動有效、什麼沒用
- 🔄 建立可重複的改進流程
- 📚 累積 context 設計知識

**立即開始：**
```bash
python context_visualizer.py
```

---

**Happy Context Engineering! 🚀**

有問題？查看相關文檔或直接修改代碼實驗！
