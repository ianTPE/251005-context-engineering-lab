"""
Context Engineering Experiment - TRUE Responses API
====================================================
使用真正的 OpenAI Responses API (client.responses.create)

重要更正：
- Responses API 使用 POST /v1/responses
- 輸入為 'input' (字串) 而非 'messages' (陣列)
- 輸出為 'output_text' 而非 'choices[0].message.content'
- 支援原生 MCP 工具和 web_search
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
    "這支耳機音質不錯，但藍牙常常斷線。",

    "The keyboard feels great, but the battery dies too fast.",
    
    "相機畫質很棒，可是夜拍對焦很慢。"

    "我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，需要重新配對才能使用，這點真的很困擾。",
    
    "The mechanical keyboard I purchased has excellent build quality with a satisfying tactile feedback that makes typing a pleasure. However, I'm quite disappointed with the battery life - it only lasts about 3-4 days with the RGB lighting on, which is far shorter than the advertised 2 weeks. I find myself charging it constantly.",
    
    "這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。",
    
    "I've been using this wireless mouse for gaming and productivity work for the past month. The ergonomic design is comfortable for long sessions, and the precision is excellent for both gaming and design work. The only downside is that the left click button has started developing a double-click issue, which is frustrating during important tasks.",
    
    "這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。"
]

# ============================================================================
# Responses API 的 Context 設計
# ============================================================================
# 注意：Responses API 使用單一 'input' 字串，而非 messages 陣列
# Few-shot 必須直接在 input 中以文字形式提供

def build_context_a_input(user_sentence):
    """Context A: Baseline"""
    return f"""Extract sentiment (positive/neutral/negative), product, and issue from this sentence.
Return as JSON.

Sentence: {user_sentence}"""


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
    """Context C: Few-shot (text-based, 因為 Responses API 只接受單一 input 字串)"""
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


# ============================================================================
# Responses API Calling Function
# ============================================================================

def call_responses_api(input_text, model="gpt-4o"):
    """
    使用真正的 Responses API
    
    注意：
    1. 使用 client.responses.create() 而非 client.chat.completions.create()
    2. 參數是 'input' 而非 'messages'
    3. 回傳是 response.output_text 而非 response.choices[0].message.content
    """
    try:
        response = client.responses.create(
            model=model,
            input=input_text
        )
        return response.output_text
    except AttributeError as e:
        # 如果 SDK 版本不支援 responses.create，提供友善錯誤訊息
        return f"ERROR: Your OpenAI SDK version doesn't support responses.create(). Please upgrade: pip install --upgrade openai"
    except Exception as e:
        return f"ERROR: {str(e)}"


# ============================================================================
# Scoring and Evaluation (同之前)
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


def eval_context(tag, input_builder, verbose=True):
    """Evaluate a context strategy using Responses API"""
    if verbose:
        print(f"\n{'='*70}")
        print(f"  {tag}")
        print(f"{'='*70}\n")
    
    results = []
    total_score = 0
    
    for i, test_sentence in enumerate(TESTS, 1):
        # Build input using the provided builder function
        input_text = input_builder(test_sentence)
        
        # Show input structure for Context C (few-shot)
        if verbose and "Few-shot" in tag and i == 1:
            print(f"📨 Input structure:")
            print(f"   Using text-based few-shot (Responses API limitation)")
            print(f"   Input length: {len(input_text)} chars\n")
        
        # Call Responses API
        output = call_responses_api(input_text)
        
        # Check for SDK error
        if output.startswith("ERROR: Your OpenAI SDK"):
            print(f"\n⚠️  {output}")
            print("\n💡 Note: Responses API is available but may require SDK version >= 1.50.0")
            print("   This experiment will show you what the code SHOULD look like.")
            return None
        
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
    """Run the complete A/B/C experiment with TRUE Responses API"""
    print("\n" + "="*70)
    print("  CONTEXT ENGINEERING EXPERIMENT")
    print("  Using TRUE OpenAI Responses API (client.responses.create)")
    print("="*70)
    print("\n💡 Key Differences from Chat Completions:")
    print("   - Uses 'input' (string) instead of 'messages' (array)")
    print("   - Returns 'output_text' instead of 'choices[0].message.content'")
    print("   - Supports native MCP tools and web_search")
    print("   - Represents OpenAI's future direction\n")
    
    # Run all three context versions
    results_a = eval_context(
        "A: Baseline (minimal instruction)",
        build_context_a_input
    )
    
    # If SDK error, exit gracefully
    if results_a is None:
        return
    
    results_b = eval_context(
        "B: Rules-based (strict format)",
        build_context_b_input
    )
    
    results_c = eval_context(
        "C: Few-shot (text-based, due to Responses API design)",
        build_context_c_input
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
    print("TRUE Responses API Characteristics:")
    print("-"*70)
    print("1. ✅ Simpler API surface (single 'input' parameter)")
    print("2. ✅ Built-in tool support (MCP, web_search)")
    print("3. ✅ Optimized for agentic workflows")
    print("4. ⚠️  Few-shot must be text-based (no message array)")
    print("5. ✅ Future-proof (OpenAI's recommended direction)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"experiment_results_true_responses_api_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "api_version": "TRUE Responses API (POST /v1/responses)",
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
        print("\n" + "="*70)
        print("  IMPORTANT NOTE")
        print("="*70)
        print("\nThis script uses the TRUE OpenAI Responses API:")
        print("  - Endpoint: POST /v1/responses")
        print("  - Method: client.responses.create()")
        print("  - SDK requirement: openai >= 1.50.0 (estimated)")
        print("\nIf you encounter SDK errors, this demonstrates the")
        print("CORRECT way to use Responses API for future reference.\n")
        
        run_experiment()
        
        print("\n" + "="*70)
        print("  API COMPARISON SUMMARY")
        print("="*70)
        print("\nChat Completions API (current mainstream):")
        print("  client.chat.completions.create(messages=[...])")
        print("  → response.choices[0].message.content")
        print("\nResponses API (future direction):")
        print("  client.responses.create(input='...')")
        print("  → response.output_text")
        print("\n→ Responses API is simpler and more powerful! ✨")
        
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
