# 🚀 Context 可視化工具 - 5 分鐘快速開始

## 🎯 這個工具是什麼？

**一句話說明**：就像 `git diff` 讓你看到代碼變化，這個工具讓你看到 **AI 的 context（上下文）如何演變**，以及這些變化如何影響 AI 的回應。

## 📸 預覽效果

### 1. Context 演變時間軸
```
📈 Context Evolution Timeline

┌────────┬──────────────────────┬────────┬──────────┐
│ Step   │ Context Name         │ Tokens │ Δ Tokens │
├────────┼──────────────────────┼────────┼──────────┤
│ #0     │ Baseline             │     15 │          │
│ #1     │ + Rules              │     63 │      +48 │
│ #2     │ + Examples           │    125 │      +62 │
└────────┴──────────────────────┴────────┴──────────┘
```

### 2. Context Diff（就像 git diff）
```diff
--- Context A (Baseline)
+++ Context B (Rules-based)
 You are a sentiment analyzer.
-Extract product info from this review.
+
+Extract the following information:
+- sentiment: "positive", "neutral", or "negative"
+- product: the product name
+- issue: description of any issues
```

### 3. 回應質量比較
```
🎯 Response Comparison

┌──────────────────────┬───────┬─────────────────────┐
│ Context              │ Score │ Preview             │
├──────────────────────┼───────┼─────────────────────┤
│ Baseline             │  50%  │ {"sentiment": ...   │
│ + Rules              │  80%  │ {"sentiment": ...   │
│ + Examples (Few-shot)│ 100%  │ {"sentiment": ...   │
└──────────────────────┴───────┴─────────────────────┘
```

## ⚡ 3 步驟開始

### 步驟 1: 安裝依賴

```bash
pip install rich tiktoken openai python-dotenv
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 步驟 2: 運行演示（無需 API）

```bash
python context_visualizer.py
```

這會展示所有功能，使用模擬數據。

### 步驟 3: 運行真實實驗（需要 OpenAI API）

```bash
# 1. 設置 API key（如果還沒設置）
# 方式 A: 環境變數 (PowerShell)
$env:OPENAI_API_KEY='sk-your-key-here'

# 方式 B: 創建 .env 文件
# 將 API key 寫入 .env 文件

# 2. 運行真實實驗
python context_visualizer_live.py
```

## 🎓 實際應用範例

### 場景：改進產品評論分析

**問題**：AI 沒有正確提取產品資訊

**步驟 1: 測試 Baseline**
```python
from context_visualizer import ContextVisualizer

viz = ContextVisualizer()

baseline = "Extract product info from this review."
viz.add_snapshot("Baseline", baseline)

# 測試回應: {"product": ""} ❌ 空的！
viz.add_response("Baseline", '{"product": ""}', score=0.3)
```

**步驟 2: 加入明確規則**
```python
rules_version = """Extract the following:
- sentiment: must be "positive", "neutral", or "negative"
- product: the product name (string)
- issue: any issues (string or empty)

Output valid JSON."""

viz.add_snapshot("+ Rules", rules_version)

# 測試回應: {"sentiment": "negative", "product": "camera"} ✅ 好多了！
viz.add_response("+ Rules", '{"sentiment": "negative", "product": "camera"}', score=0.7)
```

**步驟 3: 加入範例（Few-shot）**
```python
fewshot_version = rules_version + """

Examples:

Input: "這支耳機音質不錯，但藍牙常常斷線。"
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth"}

Input: "The keyboard feels great, battery dies fast."
Output: {"sentiment": "negative", "product": "keyboard", "issue": "battery life"}"""

viz.add_snapshot("+ Examples", fewshot_version)

# 測試回應: 完美！ ✅
viz.add_response("+ Examples", 
                 '{"sentiment": "negative", "product": "camera", "issue": "slow focus"}', 
                 score=1.0)
```

**步驟 4: 查看演變和差異**
```python
# 演變時間軸
viz.show_evolution()

# Baseline vs Rules
viz.show_diff(0, 1)

# Rules vs Few-shot
viz.show_diff(1, 2)

# 回應質量比較
viz.show_response_comparison()

# 導出結果
viz.export_comparison()  # 保存到 JSON
```

## 📊 你會看到什麼

### 1. 清楚的改進軌跡
```
Baseline (30% score)
    ↓ +48 tokens (加入規則)
+ Rules (70% score)
    ↓ +62 tokens (加入範例)
+ Examples (100% score) ✅
```

### 2. 具體的變更內容
```diff
+ Added: Explicit field definitions
+ Added: Output format constraints
+ Added: 2 concrete examples
Result: +110 tokens, +70% accuracy
```

### 3. 實際回應對比
```
Baseline:    {"product": ""}                    ❌ 空白
+ Rules:     {"sentiment": "negative", ...}     ⚠️  缺 issue
+ Examples:  {"sentiment": "negative", ...}     ✅ 完整
```

## 💡 常見用途

### ✅ Prompt 調試
發現哪個改動導致 AI 行為變化

### ✅ A/B 測試
比較多個 prompt 策略的實際效果

### ✅ Token 優化
找到最佳的 token/質量平衡點

### ✅ 團隊協作
分享 context 改進歷程和實驗結果

### ✅ 文檔化
記錄為什麼選擇特定的 prompt 設計

## 🔧 自定義你的實驗

### 修改測試案例

編輯 `context_visualizer_live.py`：

```python
TESTS = [
    "Your test case 1",
    "Your test case 2",
    "Your test case 3"
]
```

### 修改 Context 策略

```python
CTX_A = "Your baseline prompt"

CTX_B = "Your improved prompt with rules"

CTX_C = "Your few-shot prompt with examples"
```

### 自定義評分邏輯

```python
def score_response(response: str) -> float:
    # 你的評分邏輯
    score = 0.0
    
    # 例如：檢查是否包含特定欄位
    if "field1" in response:
        score += 0.5
    if "field2" in response:
        score += 0.5
    
    return score
```

## 📁 輸出文件

運行後會產生兩個文件：

### 1. `context_comparison_[timestamp].json`
包含所有 context 快照和元數據

### 2. `live_experiment_[timestamp].json`
包含完整的實驗結果和分數

這些文件可以：
- 分享給團隊成員
- 版本控制（git）
- 用於生成報告
- 追蹤長期改進

## 🎯 核心概念

### Context = AI 的"工作指南"

就像你給人類的工作說明一樣，給 AI 的 context 決定了它的工作品質。

**Bad Context:**
```
"分析這個評論"
```
→ AI 不知道要提取什麼，怎麼格式化

**Good Context:**
```
"從評論中提取：
1. sentiment (positive/neutral/negative)
2. product (產品名稱)
3. issue (問題描述)

輸出 JSON 格式

範例：
Input: "耳機很棒但藍牙會斷"
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth"}
```
→ AI 知道該做什麼，有明確參考

### Context Engineering = 優化工作指南

這個工具幫助你：
1. **追蹤**每次改動
2. **比較**不同版本
3. **測量**實際效果
4. **迭代**改進策略

## 🚀 下一步

### 初學者
- ✅ 運行演示版本
- ✅ 閱讀輸出結果
- ✅ 理解 diff 顯示

### 進階用戶
- ✅ 運行真實 API 版本
- ✅ 修改測試案例
- ✅ 自定義評分邏輯
- ✅ 整合到自己的項目

### 專家級
- ✅ 與 MCP 整合
- ✅ 建立 context 知識庫
- ✅ 實現自動優化循環
- ✅ 追蹤長期改進趨勢

## 📚 更多資源

- [完整使用指南](./VISUALIZATION_GUIDE.md) - 詳細功能說明
- [原始實驗](./README.md) - Context Engineering Lab 基礎
- [MCP 整合](./MCP_CONTEXT_ENGINEERING.md) - 動態 context 管理

## ❓ 常見問題

### Q: 需要付費 API 嗎？
A: 演示版本（`context_visualizer.py`）不需要。真實版本需要 OpenAI API key。

### Q: 可以用於其他 LLM 嗎？
A: 可以！只需修改 API 調用部分。

### Q: Token 計數準確嗎？
A: 使用 tiktoken 庫，與 OpenAI 官方計數一致。

### Q: 可以比較超過 3 個 context 嗎？
A: 當然！`add_snapshot()` 想加幾個就加幾個。

## 🎉 開始實驗！

```bash
# 立即開始
python context_visualizer.py

# 或查看幫助
python context_visualizer.py --help
```

---

**Happy Context Engineering! 🚀**

有問題？查看 [完整文檔](./VISUALIZATION_GUIDE.md) 或修改代碼實驗！
