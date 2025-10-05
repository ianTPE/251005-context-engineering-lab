"""
Context Engineering Experiment (with .env support)
===================================================
This version loads environment variables from .env file automatically.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from {env_path}")
except ImportError:
    pass

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
    print("\nPlease set your OpenAI API key:")
    print("  Option 1: Create .env file (copy .env.example)")
    print("  Option 2: Set environment variable:")
    print("    PowerShell: $env:OPENAI_API_KEY='your-key-here'")
    print("    CMD: set OPENAI_API_KEY=your-key-here")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test sentences (mixed Chinese/English) - 5 longer, more realistic reviews
TESTS = [
    "我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，需要重新配對才能使用，這點真的很困擾。",
    
    "The mechanical keyboard I purchased has excellent build quality with a satisfying tactile feedback that makes typing a pleasure. However, I'm quite disappointed with the battery life - it only lasts about 3-4 days with the RGB lighting on, which is far shorter than the advertised 2 weeks. I find myself charging it constantly.",
    
    "這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。",
    
    "I've been using this wireless mouse for gaming and productivity work for the past month. The ergonomic design is comfortable for long sessions, and the precision is excellent for both gaming and design work. The only downside is that the left click button has started developing a double-click issue, which is frustrating during important tasks.",
    
    "這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。"
]

# Base system message
SYS_BASE = "You are a helpful assistant that extracts structured information from text."

# Context Version A: Baseline (minimal instruction)
CTX_A = """Extract sentiment (positive/neutral/negative), product, and issue from the user sentence.
Return as JSON."""

# Context Version B: Rules-based (strict formatting + constraints)
CTX_B = """Task: Extract fields from the sentence.
Return ONLY a JSON object with these exact keys: sentiment, product, issue.

Rules:
- sentiment must be one of: positive, neutral, negative
- If product is not explicit, infer the most likely product noun (e.g., 'headphones', 'keyboard')
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text, no markdown code blocks
- Use lowercase English for all field values"""

# Context Version C: Few-shot (rules + examples)
CTX_C = CTX_B + """

Examples:
Input: "這台筆電螢幕很亮,但是散熱很吵。"
Output: {"sentiment": "negative", "product": "laptop", "issue": "noisy cooling"}

Input: "These earbuds are comfortable and the mic is clear."
Output: {"sentiment": "positive", "product": "earbuds", "issue": ""}
"""


def call_model(system_prompt, user_message, model="gpt-4o-mini"):
    """Call OpenAI Chat Completions API with given prompts."""
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
    """Try to extract JSON from text that might contain markdown code blocks."""
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
    """Score the output based on JSON validity and schema compliance."""
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


def eval_context(tag, context_prompt, verbose=True):
    """Evaluate a specific context version against all test sentences."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"  {tag}")
        print(f"{'='*60}\n")
    
    results = []
    total_score = 0
    
    for i, test_sentence in enumerate(TESTS, 1):
        full_prompt = f"{context_prompt}\n\nSentence: {test_sentence}"
        output = call_model(SYS_BASE, full_prompt)
        score, parsed, error = score_json(output)
        total_score += score
        
        result = {
            "test_id": i,
            "input": test_sentence,
            "output": output,
            "parsed": parsed,
            "score": score,
            "error": error
        }
        results.append(result)
        
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
    """Run the complete A/B/C experiment."""
    print("\n" + "="*60)
    print("  CONTEXT ENGINEERING EXPERIMENT")
    print("  Task: Extract structured sentiment from product reviews")
    print("="*60)
    
    results_a = eval_context("A: Baseline (minimal instruction)", CTX_A)
    results_b = eval_context("B: Rules-based (strict format)", CTX_B)
    results_c = eval_context("C: Few-shot (rules + examples)", CTX_C)
    
    print("\n" + "="*60)
    print("  SUMMARY COMPARISON")
    print("="*60 + "\n")
    
    comparison = [
        ("Context A (Baseline)", results_a["success_rate"]),
        ("Context B (Rules)", results_b["success_rate"]),
        ("Context C (Few-shot)", results_c["success_rate"])
    ]
    
    for name, rate in comparison:
        bar = "█" * int(rate * 20)
        print(f"{name:30s} {bar:20s} {rate*100:5.1f}%")
    
    print("\n" + "-"*60)
    print("Key Findings:")
    print("-"*60)
    
    if results_c["success_rate"] > results_b["success_rate"]:
        print("✓ Few-shot examples improved consistency over rules alone")
    if results_b["success_rate"] > results_a["success_rate"]:
        print("✓ Explicit rules improved reliability over baseline")
    if results_c["success_rate"] == 1.0:
        print("✓ Few-shot context achieved 100% success rate!")
    elif results_c["success_rate"] < 1.0:
        print(f"⚠ Few-shot still has {(1-results_c['success_rate'])*100:.0f}% failure rate")
    
    print("\nConclusion: More structured context (rules + examples)")
    print("typically yields more consistent and reliable outputs.")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"experiment_results_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
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
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
