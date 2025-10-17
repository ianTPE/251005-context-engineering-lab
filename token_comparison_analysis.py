"""
Token Usage Analysis: Rules-based vs Few-shot
==============================================
分析兩種prompt策略的token使用量差異，幫助選擇最經濟的方法
"""

import tiktoken

def build_context_b_input(user_sentence):
    """Context B: Rules-based"""
    return f"""Task: Extract fields from the sentence.
Return ONLY a JSON object with these exact keys: sentiment, product, issue.

Rules:
- sentiment must be one of: positive, neutral, negative
- If product is not explicit, infer the most likely product noun (e.g., 'headphones', 'keyboard')
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text, no markdown code blocks
- Use lowercase English for all field values

Sentence: {user_sentence}"""


def build_context_c_input(user_sentence):
    """Context C: Few-shot"""
    return f"""You are a product review analyzer. Extract sentiment, product, and issue from reviews.

Rules:
- sentiment: must be "positive", "neutral", or "negative"
- product: infer the product type in lowercase English
- issue: describe the problem, or empty string if none
- Return ONLY valid JSON with keys: sentiment, product, issue
- No markdown, no extra text

Examples:

Example 1:
Input: "這台筆電螢幕很亮，但是散熱很吵。"
Output: {{"sentiment": "negative", "product": "laptop", "issue": "noisy cooling"}}

Example 2:
Input: "These earbuds are comfortable and the mic is clear."
Output: {{"sentiment": "positive", "product": "earbuds", "issue": ""}}

Example 3:
Input: "The mouse is lightweight but clicks feel mushy."
Output: {{"sentiment": "negative", "product": "mouse", "issue": "mushy clicks"}}

Now analyze this sentence:
Input: "{user_sentence}"
Output:"""


def count_tokens(text, model="gpt-4"):
    """計算文本的token數量"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # 如果模型不存在，使用cl100k_base編碼（GPT-4系列通用）
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


def analyze_token_usage():
    """分析兩種方法的token使用量"""
    
    # 測試句子樣本（不同長度）
    test_sentences = [
        "Good product",  # 短句
        "這支耳機音質不錯，但藍牙常常斷線。",  # 中等長度
        "I've been using this wireless mouse for gaming and productivity work for the past month. The ergonomic design is comfortable for long sessions, and the precision is excellent for both gaming and design work. The only downside is that the left click button has started developing a double-click issue, which is frustrating during important tasks.",  # 長句
    ]
    
    print("=" * 80)
    print("  TOKEN USAGE ANALYSIS: Rules-based vs Few-shot")
    print("=" * 80)
    
    total_rules_tokens = 0
    total_fewshot_tokens = 0
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n📝 Test {i}: {sentence[:50]}{'...' if len(sentence) > 50 else ''}")
        print("-" * 70)
        
        # Rules-based方法
        rules_input = build_context_b_input(sentence)
        rules_tokens = count_tokens(rules_input)
        
        # Few-shot方法
        fewshot_input = build_context_c_input(sentence)
        fewshot_tokens = count_tokens(fewshot_input)
        
        # 計算差異
        diff = fewshot_tokens - rules_tokens
        diff_percent = (diff / rules_tokens) * 100
        
        print(f"Rules-based tokens:  {rules_tokens:4d}")
        print(f"Few-shot tokens:     {fewshot_tokens:4d}")
        print(f"Difference:          {diff:+4d} ({diff_percent:+5.1f}%)")
        
        total_rules_tokens += rules_tokens
        total_fewshot_tokens += fewshot_tokens
    
    # 總計
    total_diff = total_fewshot_tokens - total_rules_tokens
    avg_diff_percent = (total_diff / total_rules_tokens) * 100
    
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Total Rules-based tokens:  {total_rules_tokens:5d}")
    print(f"Total Few-shot tokens:     {total_fewshot_tokens:5d}")
    print(f"Total difference:          {total_diff:+5d} ({avg_diff_percent:+5.1f}%)")
    
    print(f"\n💰 Cost implications (假設 GPT-4 定價):")
    cost_per_1k_tokens = 0.03  # 假設價格
    rules_cost = (total_rules_tokens / 1000) * cost_per_1k_tokens
    fewshot_cost = (total_fewshot_tokens / 1000) * cost_per_1k_tokens
    cost_diff = fewshot_cost - rules_cost
    
    print(f"   Rules-based cost:  ${rules_cost:.4f}")
    print(f"   Few-shot cost:     ${fewshot_cost:.4f}")
    print(f"   Cost difference:   ${cost_diff:+.4f}")
    
    return {
        "rules_tokens": total_rules_tokens,
        "fewshot_tokens": total_fewshot_tokens,
        "difference": total_diff,
        "difference_percent": avg_diff_percent
    }


def provide_selection_strategy():
    """提供選擇策略建議"""
    print("\n" + "=" * 70)
    print("  SELECTION STRATEGY RECOMMENDATIONS")
    print("=" * 70)
    
    print("""
🎯 Token優化選擇策略：

1. 📊 **檢測階段**：
   - 先用少量樣本測試兩種方法的準確率
   - 如果準確率相同，選擇token更少的方法
   
2. 🔀 **動態選擇**：
   ```python
   def choose_prompt_strategy(task_complexity, budget_priority):
       if budget_priority == "high":
           return "rules_based"  # 通常更省token
       elif task_complexity == "high":
           return "few_shot"     # 更穩定的表現
       else:
           return "rules_based"  # 預設選擇
   ```

3. 📏 **基於輸入長度**：
   - 短句(<50字): Rules-based (差異不大)
   - 長句(>100字): 考慮Few-shot的穩定性vs成本
   
4. 🧪 **A/B測試建議**：
   - 在少量樣本上快速測試
   - 測量準確率 + token使用量
   - 計算ROI: accuracy_gain / token_cost_increase
   
5. 💡 **混合策略**：
   - 簡單案例: Rules-based
   - 複雜/邊緣案例: Few-shot
   - 動態切換門檻: 失敗2次→升級到Few-shot
""")

def create_token_aware_selector():
    """創建考慮token成本的選擇器"""
    print("""
🛠️ **實用程式碼範例**：

```python
def smart_prompt_selector(user_input, accuracy_threshold=0.95):
    \"\"\"
    智能選擇prompt策略
    \"\"\"
    # 1. 估算兩種方法的token使用量
    rules_tokens = estimate_rules_tokens(user_input)
    fewshot_tokens = estimate_fewshot_tokens(user_input)
    
    # 2. 如果token差異小(<20%)，優先選Rules-based
    token_diff_percent = (fewshot_tokens - rules_tokens) / rules_tokens
    if token_diff_percent < 0.2:
        return "rules_based"
    
    # 3. 如果差異大，需要考慮準確率提升是否值得
    # (這需要基於歷史資料的機器學習模型)
    estimated_accuracy_gain = predict_accuracy_gain(user_input)
    cost_benefit_ratio = estimated_accuracy_gain / token_diff_percent
    
    if cost_benefit_ratio > 2.0:  # 準確率提升超過成本增加2倍
        return "few_shot"
    else:
        return "rules_based"
```
""")


if __name__ == "__main__":
    # 執行token分析
    results = analyze_token_usage()
    
    # 提供選擇策略
    provide_selection_strategy()
    
    # 提供實用工具
    create_token_aware_selector()
    
    print(f"\n✅ Analysis complete! Few-shot uses {results['difference_percent']:+.1f}% more tokens than rules-based.")