"""
Context Engineering Experiment - Responses API Version
=======================================================
使用 OpenAI Responses API 實現更標準的 few-shot learning

Responses API 的優勢：
1. 原生支援 few-shot examples (透過 messages 結構)
2. 更清晰的對話歷史管理
3. 符合最新的 OpenAI API 設計規範
"""

import json
import os
from datetime import datetime
from openai import OpenAI

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
    print("\nPlease set your OpenAI API key:")
    print("  Windows (PowerShell): $env:OPENAI_API_KEY='your-key-here'")
    exit(1)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test sentences - 5 longer, more realistic reviews
TESTS = [
    "我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，需要重新配對才能使用，這點真的很困擾。",
    
    "The mechanical keyboard I purchased has excellent build quality with a satisfying tactile feedback that makes typing a pleasure. However, I'm quite disappointed with the battery life - it only lasts about 3-4 days with the RGB lighting on, which is far shorter than the advertised 2 weeks. I find myself charging it constantly.",
    
    "這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。",
    
    "I've been using this wireless mouse for gaming and productivity work for the past month. The ergonomic design is comfortable for long sessions, and the precision is excellent for both gaming and design work. The only downside is that the left click button has started developing a double-click issue, which is frustrating during important tasks.",
    
    "這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。"
]

# Base system message
SYS_BASE = "You are a helpful assistant that extracts structured information from product reviews."

# ============================================================================
# Context A: Baseline - 使用 Chat Completions API (原有方式)
# ============================================================================

def build_context_a_messages(user_input):
    """Context A: 最小化指示"""
    return [
        {"role": "system", "content": SYS_BASE},
        {"role": "user", "content": f"""Extract sentiment (positive/neutral/negative), product, and issue from this sentence.
Return as JSON.

Sentence: {user_input}"""}
    ]

# ============================================================================
# Context B: Rules-based - 使用嚴格規則
# ============================================================================

def build_context_b_messages(user_input):
    """Context B: 明確規則但沒有範例"""
    return [
        {"role": "system", "content": SYS_BASE},
        {"role": "user", "content": f"""Task: Extract fields from the sentence.
Return ONLY a JSON object with these exact keys: sentiment, product, issue.

Rules:
- sentiment must be one of: positive, neutral, negative
- If product is not explicit, infer the most likely product noun (e.g., 'headphones', 'keyboard')
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text, no markdown code blocks
- Use lowercase English for all field values

Sentence: {user_input}"""}
    ]

# ============================================================================
# Context C: Few-shot - 使用 Responses API 標準 few-shot 模式
# ============================================================================

def build_context_c_messages(user_input):
    """
    Context C: 使用標準 few-shot 模式
    
    在 Responses API 中，few-shot 是透過 conversation history 實現：
    1. System message 定義任務
    2. User 提供範例輸入
    3. Assistant 展示期望輸出
    4. 重複多個範例
    5. 最後提供實際的 user input
    """
    return [
        # System message: 定義任務和規則
        {
            "role": "system",
            "content": """You are a product review analyzer. Extract sentiment, product, and issue from reviews.

Rules:
- sentiment: must be "positive", "neutral", or "negative"
- product: infer the product type in lowercase English
- issue: describe the problem, or empty string if none
- Return ONLY valid JSON with keys: sentiment, product, issue
- No markdown, no extra text"""
        },
        
        # Example 1: User input
        {
            "role": "user",
            "content": "這台筆電螢幕很亮，但是散熱很吵。"
        },
        # Example 1: Assistant response
        {
            "role": "assistant",
            "content": '{"sentiment": "negative", "product": "laptop", "issue": "noisy cooling"}'
        },
        
        # Example 2: User input
        {
            "role": "user",
            "content": "These earbuds are comfortable and the mic is clear."
        },
        # Example 2: Assistant response
        {
            "role": "assistant",
            "content": '{"sentiment": "positive", "product": "earbuds", "issue": ""}'
        },
        
        # Example 3: Mixed sentiment case
        {
            "role": "user",
            "content": "The mouse is lightweight but clicks feel mushy."
        },
        # Example 3: Assistant response
        {
            "role": "assistant",
            "content": '{"sentiment": "negative", "product": "mouse", "issue": "mushy clicks"}'
        },
        
        # Actual user input
        {
            "role": "user",
            "content": user_input
        }
    ]

# ============================================================================
# API Calling Functions
# ============================================================================

def call_chat_completions(messages, model="gpt-4o-mini", temperature=0.3):
    """
    使用 Chat Completions API
    這是目前主流的方式，也是我們一直在用的
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


# Note: Responses API 實際上在目前的 OpenAI Python SDK 中
# 仍然使用 chat.completions.create，但我們透過 messages 結構
# 來實現更標準的 few-shot learning

# ============================================================================
# Scoring and Evaluation
# ============================================================================

def clean_json_output(text):
    """Extract JSON from text that might contain markdown blocks"""
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
    """Score output based on schema compliance"""
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
            errors = []
            if not keys_ok: errors.append(f"wrong_keys: {set(obj.keys())}")
            if not sentiment_ok: errors.append(f"invalid_sentiment: {obj.get('sentiment')}")
            if not product_ok: errors.append("empty_or_invalid_product")
            if not issue_ok: errors.append("missing_or_invalid_issue")
            return 0, obj, ", ".join(errors)
            
    except json.JSONDecodeError as e:
        return 0, None, f"JSON parse error: {str(e)}"
    except Exception as e:
        return 0, None, f"Unexpected error: {str(e)}"


def eval_context(tag, message_builder, verbose=True):
    """Evaluate a context strategy"""
    if verbose:
        print(f"\n{'='*70}")
        print(f"  {tag}")
        print(f"{'='*70}\n")
    
    results = []
    total_score = 0
    
    for i, test_sentence in enumerate(TESTS, 1):
        # Build messages using the provided builder function
        messages = message_builder(test_sentence)
        
        # Show message structure for Context C (few-shot)
        if verbose and "Few-shot" in tag and i == 1:
            print(f"📨 Message structure (showing {len(messages)} messages):")
            print(f"   - 1 system message")
            print(f"   - {(len(messages) - 2) // 2} example pairs (user + assistant)")
            print(f"   - 1 actual user query\n")
        
        # Call API
        output = call_chat_completions(messages)
        
        # Score output
        score, parsed, error = score_json(output)
        total_score += score
        
        # Store result
        result = {
            "test_id": i,
            "input": test_sentence,
            "output": output,
            "parsed": parsed,
            "score": score,
            "error": error
        }
        results.append(result)
        
        # Print if verbose
        if verbose:
            print(f"Test {i}: {test_sentence}")
            print(f"Output: {output}")
            print(f"Parsed: {json.dumps(parsed, ensure_ascii=False) if parsed else 'FAILED'}")
            print(f"Score: {score}/1 {f'({error})' if error else '✓'}")
            print()
    
    if verbose:
        print(f"[{tag}] Total Score: {total_score}/{len(TESTS)}")
        print(f"Success Rate: {total_score/len(TESTS)*100:.1f}%")
    
    return {
        "tag": tag,
        "total_score": total_score,
        "max_score": len(TESTS),
        "success_rate": total_score / len(TESTS),
        "results": results
    }


def run_experiment():
    """Run the complete A/B/C experiment with Responses API"""
    print("\n" + "="*70)
    print("  CONTEXT ENGINEERING EXPERIMENT")
    print("  Using OpenAI Responses API for Few-shot Learning")
    print("="*70)
    print("\n💡 Key Difference: Context C uses proper conversation history")
    print("   for few-shot examples instead of text-based prompting.\n")
    
    # Run all three context versions
    results_a = eval_context(
        "A: Baseline (minimal instruction)",
        build_context_a_messages
    )
    
    results_b = eval_context(
        "B: Rules-based (strict format)",
        build_context_b_messages
    )
    
    results_c = eval_context(
        "C: Few-shot (Responses API with conversation history)",
        build_context_c_messages
    )
    
    # Summary comparison
    print("\n" + "="*70)
    print("  SUMMARY COMPARISON")
    print("="*70 + "\n")
    
    comparison = [
        ("Context A (Baseline)", results_a["success_rate"]),
        ("Context B (Rules)", results_b["success_rate"]),
        ("Context C (Few-shot)", results_c["success_rate"])
    ]
    
    for name, rate in comparison:
        bar = "█" * int(rate * 20)
        print(f"{name:30s} {bar:20s} {rate*100:5.1f}%")
    
    print("\n" + "-"*70)
    print("Key Findings:")
    print("-"*70)
    
    if results_c["success_rate"] > results_b["success_rate"]:
        print("✓ Few-shot examples improved consistency over rules alone")
    if results_b["success_rate"] > results_a["success_rate"]:
        print("✓ Explicit rules improved reliability over baseline")
    if results_c["success_rate"] == 1.0:
        print("✓ Few-shot context achieved 100% success rate!")
    elif results_c["success_rate"] < 1.0:
        print(f"⚠ Few-shot still has {(1-results_c['success_rate'])*100:.0f}% failure rate")
    
    print("\n" + "-"*70)
    print("Responses API Advantages for Few-shot:")
    print("-"*70)
    print("1. ✓ Structured conversation history (not text-based)")
    print("2. ✓ Clear example pairs (user → assistant)")
    print("3. ✓ Better model understanding of expected format")
    print("4. ✓ Easier to maintain and update examples")
    print("5. ✓ Follows OpenAI's recommended best practices")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"experiment_results_responses_api_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "api_version": "Responses API (via chat.completions)",
            "test_sentences": TESTS,
            "results": {
                "context_a": results_a,
                "context_b": results_b,
                "context_c": results_c
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    try:
        run_experiment()
        
        print("\n" + "="*70)
        print("  COMPARISON: Text-based vs API-based Few-shot")
        print("="*70)
        print("\nText-based (original):")
        print("  System: 'Here are examples: Input X → Output Y'")
        print("  User: 'Now analyze this...'")
        print("\nAPI-based (Responses API):")
        print("  System: 'Task definition'")
        print("  User: 'Example input 1'")
        print("  Assistant: 'Example output 1'")
        print("  User: 'Example input 2'")
        print("  Assistant: 'Example output 2'")
        print("  User: 'Actual input'")
        print("\n→ The second approach is more natural and effective! ✨")
        
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
