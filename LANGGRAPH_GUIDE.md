# LangGraph Context Engineering 實驗指南 🎯

## 🎯 什麼是 LangGraph？

**LangGraph** 是一個用於構建有狀態、多步驟 LLM 應用的框架。它將複雜的工作流程轉換為**圖結構**（Graph），讓流程更加：
- ✅ **清晰** - 每個步驟是一個節點（Node）
- ✅ **可控** - 明確定義狀態（State）和邊（Edge）
- ✅ **可擴展** - 容易添加新節點或分支邏輯

## 🆚 為什麼用 LangGraph？

### 傳統方式（Sequential）
```python
# 依序執行，狀態分散
result_a = test_context_a(sentence)
result_b = test_context_b(sentence)
result_c = test_context_c(sentence)

# 難以追蹤狀態
# 難以添加分支邏輯
# 難以可視化流程
```

### LangGraph 方式（Graph-based）
```python
# 定義 State
class State(TypedDict):
    sentence: str
    results: Dict
    scores: Dict

# 定義 Nodes
def node_a(state): ...
def node_b(state): ...
def node_c(state): ...

# 建立 Graph
graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_node("c", node_c)

# 定義流程
graph.add_edge("a", "b")
graph.add_edge("b", "c")

# 執行
result = graph.invoke(initial_state)
```

**優勢：**
- ✅ 狀態集中管理
- ✅ 流程清晰可見
- ✅ 容易添加條件分支
- ✅ 支援可視化

---

## 🏗️ 我們的 LangGraph 設計

### 1. State Schema（狀態定義）

```python
class ContextEngineringState(TypedDict):
    # 輸入
    test_sentence: str       # 測試句子
    test_id: int            # 測試 ID
    
    # 三種 Context 定義
    context_a: str          # Baseline
    context_b: str          # Rules-based
    context_c: str          # Few-shot
    
    # 每個策略的輸出
    result_a: Dict          # Context A 結果
    result_b: Dict          # Context B 結果
    result_c: Dict          # Context C 結果
    
    # 評分
    scores: Dict[str, float]  # 各策略分數
    
    # 當前階段
    current_step: str       # 追蹤進度
```

### 2. Nodes（節點）

**三個主要節點，每個負責測試一種策略：**

```python
def run_context_a(state):
    """Node A: 測試 Baseline Context"""
    response = call_openai_api(state["context_a"], state["test_sentence"])
    score = score_response(response)
    
    state["result_a"] = {"response": response, "score": score}
    state["scores"]["Context A"] = score
    state["current_step"] = "completed_a"
    
    return state

# 同樣邏輯適用於 run_context_b 和 run_context_c
```

### 3. Graph Structure（圖結構）

```
┌─────────┐
│  START  │
└────┬────┘
     │
     v
┌─────────────┐
│  Context A  │ (Baseline)
│  Node       │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Context B  │ (Rules-based)
│  Node       │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Context C  │ (Few-shot)
│  Node       │
└──────┬──────┘
       │
       v
   ┌───────┐
   │  END  │
   └───────┘
```

### 4. Code 實現

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
    
    # 添加邊：定義執行順序
    workflow.add_edge("context_a", "context_b")
    workflow.add_edge("context_b", "context_c")
    workflow.add_edge("context_c", END)
    
    # 編譯 graph
    app = workflow.compile()
    
    return app
```

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install langgraph langchain-core
```

或更新 requirements.txt 後：
```bash
pip install -r requirements.txt
```

### 2. 執行實驗

```bash
python context_experiment_langgraph.py
```

### 3. 輸出示例

```
╔══════════════════════════════════════════════════════════╗
║  LangGraph Context Engineering Experiment               ║
║  Using StateGraph to orchestrate A/B/C testing          ║
╚══════════════════════════════════════════════════════════╝

================================================================================
🎯 LangGraph Context Engineering Experiment
================================================================================

================================================================================
📝 Test Case 1: 這支耳機音質不錯，但藍牙常常斷線。...
================================================================================

🔵 Testing Context A (Baseline) for test #1...
   Score: 0.0%

🟢 Testing Context B (Rules-based) for test #1...
   Score: 100.0%

🟡 Testing Context C (Few-shot) for test #1...
   Score: 100.0%

📊 Summary for Test 1:
   Context A: 0.0%
   Context B: 100.0%
   Context C: 100.0%

================================================================================
📈 FINAL RESULTS
================================================================================

🎯 Average Scores:
   Context A (Baseline)           ░░░░░░░░░░░░░░░░░░░░ 0.0%
   Context B (Rules-based)        ████████████████████ 100.0%
   Context C (Few-shot)           ████████████████████ 100.0%

✅ Results saved to: langgraph_experiment_20251006_170530.json

🏆 Best Strategy: Context B (Rules-based) (100.0%)
```

---

## 🎨 進階：條件分支

LangGraph 的強大之處在於**條件邊**（Conditional Edges）。例如：

### 動態選擇策略

```python
def route_next_strategy(state):
    """根據前一個結果決定下一步"""
    if state["scores"]["Context A"] >= 0.8:
        # 如果 Baseline 已經很好，跳過其他測試
        return END
    else:
        # 否則繼續測試
        return "context_b"

# 添加條件邊
workflow.add_conditional_edges(
    "context_a",
    route_next_strategy,
    {
        "context_b": "context_b",
        END: END
    }
)
```

### 智能重試

```python
def run_context_with_retry(state):
    """如果失敗，自動重試"""
    max_retries = 3
    
    for attempt in range(max_retries):
        response = call_openai_api(state["context"], state["sentence"])
        score = score_response(response)
        
        if score >= 0.8:
            # 成功
            state["result"] = response
            state["next"] = "proceed"
            return state
    
    # 失敗後嘗試更強的 context
    state["next"] = "use_fewshot"
    return state

workflow.add_conditional_edges(
    "initial_test",
    lambda s: s["next"],
    {
        "proceed": "next_step",
        "use_fewshot": "context_c"
    }
)
```

---

## 📊 與其他方法比較

| 特性 | Sequential | LangGraph | 傳統 Workflow |
|------|-----------|-----------|--------------|
| **狀態管理** | 分散 | 集中 ✅ | 分散 |
| **可視化** | ❌ | ✅ | 部分 |
| **條件邏輯** | 困難 | 容易 ✅ | 中等 |
| **可擴展性** | 低 | 高 ✅ | 中等 |
| **除錯** | 困難 | 容易 ✅ | 困難 |
| **學習曲線** | 低 | 中 | 高 |

---

## 🛠️ 實際應用場景

### 1. **多策略 A/B Testing**
```python
# 並行測試多個策略
graph.add_node("strategy_a", test_a)
graph.add_node("strategy_b", test_b)
graph.add_node("strategy_c", test_c)
graph.add_node("compare", compare_results)

# 同時執行 A、B、C
graph.add_edge("start", "strategy_a")
graph.add_edge("start", "strategy_b")
graph.add_edge("start", "strategy_c")

# 收斂到比較節點
graph.add_edge("strategy_a", "compare")
graph.add_edge("strategy_b", "compare")
graph.add_edge("strategy_c", "compare")
```

### 2. **自適應策略選擇**
```python
def choose_strategy(state):
    """根據任務複雜度選擇策略"""
    if state["task_complexity"] == "simple":
        return "baseline"
    elif state["task_complexity"] == "medium":
        return "rules_based"
    else:
        return "few_shot"

graph.add_conditional_edges(
    "analyze_task",
    choose_strategy,
    {
        "baseline": "context_a",
        "rules_based": "context_b",
        "few_shot": "context_c"
    }
)
```

### 3. **失敗重試機制**
```python
def check_quality(state):
    """檢查輸出質量"""
    if state["score"] >= 0.9:
        return "success"
    elif state["retries"] < 3:
        return "retry"
    else:
        return "fallback"

graph.add_conditional_edges(
    "test_strategy",
    check_quality,
    {
        "success": END,
        "retry": "test_strategy",  # 重試
        "fallback": "use_stronger_model"  # 使用更強模型
    }
)
```

---

## 📈 下一步

### 初學者
1. ✅ 運行基本實驗：`python context_experiment_langgraph.py`
2. ✅ 理解 State、Node、Edge 概念
3. ✅ 查看生成的 JSON 結果

### 進階用戶
1. ✅ 添加條件邊實現智能路由
2. ✅ 實現並行節點執行
3. ✅ 添加重試邏輯
4. ✅ 可視化 Graph 結構

### 專家級
1. ✅ 整合 Context Visualizer
2. ✅ 實現動態 Context 生成
3. ✅ 多模型比較（GPT-4 vs Claude）
4. ✅ 建立 Context 自動優化循環

---

## 🔗 相關資源

- 📚 [LangGraph 官方文檔](https://langchain-ai.github.io/langgraph/)
- 🎓 [LangGraph 教程](https://langchain-ai.github.io/langgraph/tutorials/)
- 🎨 [Context Visualizer](./QUICKSTART_VISUALIZATION.md)
- 📖 [原始實驗](./README.md)

---

## 🐛 故障排除

### ModuleNotFoundError: No module named 'langgraph'

```bash
pip install langgraph langchain-core
```

### State 更新沒生效

確保 Node 函數**返回更新後的 state**：
```python
def my_node(state):
    state["result"] = "new value"
    return state  # ⚠️ 必須返回！
```

### 無限循環

檢查是否有邊指向自己：
```python
# ❌ 錯誤：無限循環
graph.add_edge("node_a", "node_a")

# ✅ 正確：添加終止條件
graph.add_conditional_edges(
    "node_a",
    lambda s: "node_a" if s["retry"] < 3 else END
)
```

---

## 🎉 總結

LangGraph 讓 Context Engineering 從**線性流程**變成**靈活圖結構**：

- ✅ 狀態集中管理
- ✅ 流程清晰可見
- ✅ 容易添加複雜邏輯
- ✅ 支援並行和條件執行
- ✅ 易於除錯和維護

**開始實驗：**
```bash
python context_experiment_langgraph.py
```

---

**Happy Graph Building! 🚀**
