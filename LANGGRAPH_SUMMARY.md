# 🎯 LangGraph Context Engineering - 完整總結

## 📌 什麼問題被解決了？

您問：
> "想用 LangGraph？給你最小思路...把 A/B/C 當成三個 Node，用 StateGraph 串起來"

**答案：我們成功實現了！** ✅

---

## 🏗️ 實現架構

### 核心概念

```
傳統方式（Sequential）          LangGraph 方式（Graph-based）
=====================          =========================

result_a = test_a()              ┌─────────┐
result_b = test_b()              │  START  │
result_c = test_c()              └────┬────┘
                                      │
❌ 狀態分散                           v
❌ 難以追蹤                      ┌─────────┐
❌ 不易擴展                      │ Node A  │ ← State 管理
                                 └────┬────┘
                                      │
                                      v
                                 ┌─────────┐
                                 │ Node B  │ ← State 更新
                                 └────┬────┘
                                      │
                                      v
                                 ┌─────────┐
                                 │ Node C  │ ← State 完成
                                 └────┬────┘
                                      │
                                      v
                                  ┌───────┐
                                  │  END  │
                                  └───────┘

                                 ✅ 狀態集中
                                 ✅ 流程清晰
                                 ✅ 易於擴展
```

---

## 📊 實驗結果

### 運行輸出

```
╔══════════════════════════════════════════════════════════╗
║  LangGraph Context Engineering Experiment               ║
║  Using StateGraph to orchestrate A/B/C testing          ║
╚══════════════════════════════════════════════════════════╝

📝 Test Case 1: 這支耳機音質不錯，但藍牙常常斷線。

🔵 Testing Context A (Baseline) for test #1...
   Score: 0.0%
🟢 Testing Context B (Rules-based) for test #1...
   Score: 100.0%
🟡 Testing Context C (Few-shot) for test #1...
   Score: 100.0%

[... 2 more tests ...]

📈 FINAL RESULTS

🎯 Average Scores:
   Context A (Baseline)           ░░░░░░░░░░░░░░░░░░░░ 0.0%
   Context B (Rules-based)        ████████████████████ 100.0%
   Context C (Few-shot)           ████████████████████ 100.0%

🏆 Best Strategy: Context B (Rules-based) (100.0%)
```

### 關鍵發現

| Context | 分數 | 觀察 |
|---------|------|------|
| **Baseline** | 0% | ❌ 完全失敗，非 JSON 格式 |
| **Rules** | 100% | ✅ 完美，有明確規則 |
| **Few-shot** | 100% | ✅ 完美，額外有範例參考 |

**結論：** Rules-based 已經足夠，Few-shot 提供額外穩定性。

---

## 🎨 實現細節

### 1. State Schema

```python
class ContextEngineringState(TypedDict):
    # 輸入
    test_sentence: str          # 測試句子
    test_id: int               # 測試編號
    
    # Context 定義
    context_a: str             # Baseline
    context_b: str             # Rules-based
    context_c: str             # Few-shot
    
    # 結果
    result_a: Dict             # Context A 輸出
    result_b: Dict             # Context B 輸出
    result_c: Dict             # Context C 輸出
    
    # 評分
    scores: Dict[str, float]   # 各策略分數
    
    # 追蹤
    current_step: str          # 當前階段
```

**優勢：**
- ✅ 所有狀態集中管理
- ✅ 類型明確（TypedDict）
- ✅ 易於追蹤和除錯

### 2. Node Functions

```python
def run_context_a(state: ContextEngineringState) -> ContextEngineringState:
    """Node A: 測試 Baseline Context"""
    print(f"🔵 Testing Context A...")
    
    # 調用 API
    response = call_openai_api(state["context_a"], state["test_sentence"])
    
    # 評分
    score = score_response(response)
    
    # 更新 State
    state["result_a"] = {"response": response, "score": score}
    state["scores"]["Context A"] = score
    state["current_step"] = "completed_a"
    
    return state  # ⚠️ 必須返回 state！
```

**關鍵點：**
- ✅ 接收 state，更新 state，返回 state
- ✅ 清晰的輸入/輸出
- ✅ 單一職責（只測試一個 context）

### 3. Graph Construction

```python
def create_context_engineering_graph():
    # 創建 StateGraph
    workflow = StateGraph(ContextEngineringState)
    
    # 添加節點
    workflow.add_node("context_a", run_context_a)
    workflow.add_node("context_b", run_context_b)
    workflow.add_node("context_c", run_context_c)
    
    # 設置起點
    workflow.set_entry_point("context_a")
    
    # 定義執行流程（邊）
    workflow.add_edge("context_a", "context_b")  # A → B
    workflow.add_edge("context_b", "context_c")  # B → C
    workflow.add_edge("context_c", END)          # C → END
    
    # 編譯
    return workflow.compile()
```

**流程圖：**
```
START → context_a → context_b → context_c → END
        (Baseline)  (Rules)     (Few-shot)
```

---

## 🆚 LangGraph vs 傳統方式

### 代碼比較

**傳統方式：**
```python
# 分散的狀態
results_a = []
results_b = []
results_c = []

for test in tests:
    # 重複的邏輯
    result_a = test_context_a(test)
    results_a.append(result_a)
    
    result_b = test_context_b(test)
    results_b.append(result_b)
    
    result_c = test_context_c(test)
    results_c.append(result_c)

# 手動聚合結果
final_results = aggregate(results_a, results_b, results_c)
```

**LangGraph 方式：**
```python
# 定義一次
app = create_context_engineering_graph()

for test in tests:
    # 初始化 state
    initial_state = {
        "test_sentence": test,
        "context_a": CTX_A,
        "context_b": CTX_B,
        "context_c": CTX_C,
        # ... 其他欄位
    }
    
    # 一次執行，自動管理狀態
    final_state = app.invoke(initial_state)
    
    # 結果已經在 state 中
    results.append(final_state)
```

### 優勢對比

| 特性 | 傳統方式 | LangGraph |
|------|---------|-----------|
| **狀態管理** | 分散變數 | 集中 State ✅ |
| **流程可視化** | 難 | 易（Mermaid 圖） ✅ |
| **添加條件邏輯** | 需重構代碼 | 添加 conditional_edges ✅ |
| **並行執行** | 手動管理 | 內建支援 ✅ |
| **除錯** | 困難 | 容易（State 追蹤） ✅ |
| **可擴展性** | 低 | 高 ✅ |
| **學習曲線** | 低 | 中 |

---

## 🚀 進階應用

### 1. 條件分支

**場景：** 如果 Baseline 已經很好，跳過其他測試

```python
def route_next(state):
    if state["scores"]["Context A"] >= 0.8:
        return END  # 跳過 B 和 C
    else:
        return "context_b"  # 繼續測試

workflow.add_conditional_edges(
    "context_a",
    route_next,
    {
        "context_b": "context_b",
        END: END
    }
)
```

**效果：**
```
如果 A 好：
START → context_a → END

如果 A 不好：
START → context_a → context_b → context_c → END
```

### 2. 智能重試

**場景：** 如果某個 context 失敗，自動重試或升級

```python
def run_with_retry(state):
    max_retries = 3
    
    for attempt in range(max_retries):
        response = call_api(state["context"], state["sentence"])
        score = score_response(response)
        
        if score >= 0.8:
            state["next"] = "success"
            return state
    
    # 失敗後使用更強 context
    state["next"] = "use_fewshot"
    return state

workflow.add_conditional_edges(
    "try_baseline",
    lambda s: s["next"],
    {
        "success": "proceed",
        "use_fewshot": "context_c"
    }
)
```

### 3. 並行測試

**場景：** 同時測試 A、B、C，最後比較結果

```python
# 創建並行節點
workflow.add_node("test_a", run_context_a)
workflow.add_node("test_b", run_context_b)
workflow.add_node("test_c", run_context_c)
workflow.add_node("compare", compare_results)

# 從 START 並行到 A、B、C
workflow.add_edge(START, "test_a")
workflow.add_edge(START, "test_b")
workflow.add_edge(START, "test_c")

# 收斂到 compare
workflow.add_edge("test_a", "compare")
workflow.add_edge("test_b", "compare")
workflow.add_edge("test_c", "compare")
```

**效果：**
```
       ┌─→ test_a ─┐
START ─┼─→ test_b ─┼─→ compare → END
       └─→ test_c ─┘
```

---

## 📈 實際數據

### JSON 輸出示例

```json
{
  "timestamp": "2025-10-06T17:11:22",
  "average_scores": {
    "Context A (Baseline)": 0.0,
    "Context B (Rules-based)": 1.0,
    "Context C (Few-shot)": 1.0
  },
  "graph_structure": {
    "nodes": ["context_a", "context_b", "context_c"],
    "edges": [
      ["START", "context_a"],
      ["context_a", "context_b"],
      ["context_b", "context_c"],
      ["context_c", "END"]
    ]
  }
}
```

### 性能指標

- **總測試案例：** 3
- **每個案例測試策略：** 3 (A, B, C)
- **總 API 調用：** 9
- **執行時間：** ~15 秒
- **成功率：** 
  - Context A: 0/3 (0%)
  - Context B: 3/3 (100%)
  - Context C: 3/3 (100%)

---

## 💡 關鍵收穫

### 1. LangGraph 的價值

**不僅是語法糖，而是架構改進：**

- ✅ **狀態集中** → 更容易追蹤和除錯
- ✅ **流程明確** → 更容易理解和維護
- ✅ **擴展性強** → 更容易添加新功能
- ✅ **可視化** → 更容易溝通和文檔化

### 2. 何時使用 LangGraph？

**適合：**
- ✅ 多步驟流程（3+ 步驟）
- ✅ 需要條件邏輯
- ✅ 需要並行執行
- ✅ 複雜的狀態管理
- ✅ 團隊協作項目

**不適合：**
- ❌ 簡單的單步驟任務
- ❌ 快速原型（overengineering）
- ❌ 學習時間緊張

### 3. Context Engineering 結論

**實驗證明：**
- ❌ Baseline (無規則) → 0% 成功
- ✅ Rules-based (有規則) → 100% 成功
- ✅ Few-shot (規則+範例) → 100% 成功

**最佳實踐：**
1. **永遠使用規則** - Baseline 不可靠
2. **Few-shot 用於複雜任務** - 提供額外穩定性
3. **用 LangGraph 管理多策略** - 清晰的流程控制

---

## 🎯 立即開始

### 1. 安裝依賴

```bash
pip install langgraph langchain-core
```

### 2. 運行實驗

```bash
python context_experiment_langgraph.py
```

### 3. 查看結果

```bash
# JSON 結果文件
langgraph_experiment_TIMESTAMP.json

# 包含：
- 每個測試的詳細結果
- API 原始回應
- 評分
- Graph 結構
```

---

## 📚 相關資源

- 🎯 [LangGraph 實驗代碼](./context_experiment_langgraph.py)
- 📖 [完整使用指南](./LANGGRAPH_GUIDE.md)
- 🎨 [Context 可視化工具](./QUICKSTART_VISUALIZATION.md)
- 📊 [原始實驗](./README.md)

---

## 🎉 總結

我們成功將 **Sequential A/B/C 測試** 轉換為 **LangGraph StateGraph**：

```python
# 從這個 ❌
result_a = test_a()
result_b = test_b()
result_c = test_c()

# 到這個 ✅
graph = StateGraph(State)
graph.add_node("a", test_a)
graph.add_node("b", test_b)
graph.add_node("c", test_c)
graph.add_edge("a", "b")
graph.add_edge("b", "c")
app = graph.compile()
result = app.invoke(initial_state)
```

**核心價值：**
- 🎯 狀態集中管理
- 📊 流程清晰可見
- 🔧 易於擴展和維護
- 🚀 支援進階模式（條件、並行、重試）

---

**Happy Graph Building! 🚀**

開始你的 LangGraph 之旅：
```bash
python context_experiment_langgraph.py
```
