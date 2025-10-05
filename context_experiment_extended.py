"""
Context Engineering Experiment - Extended Test Cases
====================================================
擴展測試案例，包含各種挑戰性場景：
- Positive 評論
- Neutral 評論
- 極長評論（300+ 字）
- 短評論
- 沒有明確問題
- 多個產品
- 諷刺性評論
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

# Extended test cases - 12 cases covering various scenarios
TESTS = [
    # 1. SHORT POSITIVE (短評，純正面)
    {
        "text": "這個藍牙喇叭音質超棒，cp值很高！",
        "expected_sentiment": "positive",
        "expected_product": "speaker",
        "category": "短評-正面"
    },
    
    # 2. SHORT NEUTRAL (短評，中性描述)
    {
        "text": "This USB hub has 4 ports and works as expected.",
        "expected_sentiment": "neutral",
        "expected_product": "usb hub",
        "category": "短評-中性"
    },
    
    # 3. POSITIVE - 完全滿意的評論
    {
        "text": "我用這款筆記型電腦已經半年了，整體體驗非常棒！效能強大可以同時開很多程式，散熱系統設計得很好即使長時間使用也不會過熱，鍵盤手感舒適打字很流暢，螢幕顯示清晰色彩準確，電池續航力也很不錯，出門工作一整天都沒問題。客服態度也很好，有問題馬上解決。強烈推薦給需要高效能筆電的朋友！",
        "expected_sentiment": "positive",
        "expected_product": "laptop",
        "category": "正面-無問題"
    },
    
    # 4. NEUTRAL - 客觀描述，無明顯情感傾向
    {
        "text": "I purchased this external hard drive for backup purposes. It has 2TB storage capacity, USB 3.0 connectivity, and comes with backup software. The transfer speed is around 120MB/s, which is within the standard range for this type of device. The build quality is plastic but feels solid. It's been working for three months without any issues. Price is comparable to similar products in the market.",
        "expected_sentiment": "neutral",
        "expected_product": "external hard drive",
        "category": "中性-客觀描述"
    },
    
    # 5. VERY LONG - 極長評論（300+ 字），混合情感
    {
        "text": "我在三個月前購買了這款旗艦級智慧型手機，價格雖然不便宜但我覺得還算合理，畢竟規格真的很頂。先說優點，螢幕真的是我用過最棒的，6.7吋AMOLED面板，120Hz更新率，顏色鮮豔又不會過於濃艷，看影片和玩遊戲的體驗都非常好。拍照功能也很強大，主鏡頭5000萬畫素，拍出來的照片細節豐富，色彩還原度高，夜拍模式也處理得很好，雜訊控制得宜。處理器是最新的旗艦晶片，效能確實很強，開任何app都很流暢，多工處理也不會卡頓。不過使用一段時間後也發現了一些問題。首先是發熱問題，玩遊戲或拍攝影片超過30分鐘，手機背面就會變得很燙，雖然不至於燙手但還是讓人有點擔心。其次是電池續航，雖然官方標榜5000mAh大電池，但實際使用下來，如果常開啟5G和高更新率螢幕，大概到下午3-4點就要充電了，跟預期有落差。另外系統的UI設計我個人覺得不夠直覺，有些功能藏得很深要翻好幾層選單才找得到，這點希望之後軟體更新能改善。最後是價格，雖然規格很好，但這個價位已經可以買到其他品牌的頂規機種，所以性價比可能不是最高的選擇。整體來說是支好手機，但不是完美，如果你重視效能和螢幕品質，可以考慮，但如果在意續航和溫控，可能要三思。",
        "expected_sentiment": "neutral",  # 或 negative（因為問題較多）
        "expected_product": "smartphone",
        "category": "極長-混合情感"
    },
    
    # 6. NO CLEAR ISSUE - 負面情緒但沒有明確問題
    {
        "text": "買了這個行動電源覺得有點後悔，雖然說不上來哪裡不好，但就是感覺不太對勁，可能是我期望太高了吧，整體來說就是普通，沒有想像中那麼好用，但也還能用啦。",
        "expected_sentiment": "negative",
        "expected_product": "power bank",
        "category": "邊界-模糊問題"
    },
    
    # 7. MULTIPLE PRODUCTS - 多個產品的評論
    {
        "text": "I bought a complete home office setup including a monitor, keyboard, and mouse. The 27-inch monitor has great color accuracy and the stand is adjustable. The mechanical keyboard is satisfying to type on. However, the wireless mouse is disappointing - it's uncomfortable for long use and the battery drains quickly. Overall, two out of three products are excellent.",
        "expected_sentiment": "neutral",  # 整體混合
        "expected_product": "office setup",  # 或 mouse（主要問題）
        "category": "邊界-多產品"
    },
    
    # 8. SARCASTIC - 諷刺性評論
    {
        "text": "哇，這個充電線真是太「耐用」了，才用三個月就斷掉，品質真是「優良」！客服還說這是正常使用損耗，真是太「貼心」了。強烈「推薦」給喜歡定期買充電線的朋友！",
        "expected_sentiment": "negative",
        "expected_product": "charging cable",
        "category": "邊界-諷刺"
    },
    
    # 9. POSITIVE with minor mention - 正面為主，輕微提及缺點
    {
        "text": "This noise-cancelling headphone is absolutely fantastic! The sound quality is crystal clear with deep bass and crisp highs. The noise cancellation works like magic - I can focus completely in noisy environments. Battery lasts for 30+ hours, which is incredible. The only minor thing is the carrying case could be a bit more compact, but that's really nitpicking. Highly recommended!",
        "expected_sentiment": "positive",
        "expected_product": "headphones",
        "category": "正面-微小缺點"
    },
    
    # 10. NEGATIVE DISGUISED AS POSITIVE - 表面正面實則負面
    {
        "text": "這台空氣清淨機的外觀設計很漂亮，擺在客廳很好看，而且很安靜，開著都不知道有沒有在運作。價格雖然貴但想說一分錢一分貨就買了。結果用了兩個月，完全感覺不到空氣有變乾淨，過敏症狀一樣嚴重，換了兩次濾網也沒改善。可能只適合當裝飾品用吧。",
        "expected_sentiment": "negative",
        "expected_product": "air purifier",
        "category": "邊界-表面正面"
    },
    
    # 11. NEUTRAL with technical details - 純技術規格描述
    {
        "text": "Purchased this router for home use. Specifications: WiFi 6 (802.11ax), dual-band 2.4GHz/5GHz, maximum speed 3000Mbps, 4 Gigabit LAN ports, WPA3 security. Setup took approximately 15 minutes using the mobile app. Coverage area is adequate for a 1500 sq ft apartment. Firmware version 1.2.3 as of purchase date.",
        "expected_sentiment": "neutral",
        "expected_product": "router",
        "category": "中性-技術規格"
    },
    
    # 12. EXTREME NEGATIVE - 極度負面，多重嚴重問題
    {
        "text": "這絕對是我買過最糟糕的平板電腦！收到貨第一天螢幕就有亮點，觸控經常失靈要點好幾次才有反應，系統超級卡頓開個網頁都要等半天，電池更是笑話，充滿電只能用2小時就沒電了，而且充電時會發燙到根本不敢碰。客服態度超差，說這些都是正常現象不給退換貨。花了一萬多塊買個垃圾，根本就是詐騙！千萬不要買，除非你想找罪受！",
        "expected_sentiment": "negative",
        "expected_product": "tablet",
        "category": "極負面-多問題"
    }
]

# Base system message
SYS_BASE = "You are a helpful assistant that extracts structured information from product reviews."

# ============================================================================
# Context Definitions
# ============================================================================

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
- For positive reviews with no real issues, issue should be empty string
- For sarcastic reviews, focus on the actual negative meaning
- If product is not explicit, infer the most likely product noun
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text, no markdown code blocks
- Use lowercase English for all field values

Sentence: {user_sentence}"""


def build_context_c_input(user_sentence):
    """Context C: Few-shot with diverse examples"""
    return f"""You are a product review analyzer. Extract sentiment, product, and issue from reviews.

Rules:
- sentiment: must be "positive", "neutral", or "negative"
- product: infer the product type in lowercase English
- issue: describe the problem, or empty string if none
- Return ONLY valid JSON with keys: sentiment, product, issue
- No markdown, no extra text

Examples:

Example 1 (Positive review):
Input: "This laptop is amazing! Fast, great battery life, and the screen is beautiful."
Output: {{"sentiment": "positive", "product": "laptop", "issue": ""}}

Example 2 (Negative with issue):
Input: "這台印表機常常卡紙，而且墨水很快就用完了。"
Output: {{"sentiment": "negative", "product": "printer", "issue": "frequent paper jams and fast ink consumption"}}

Example 3 (Neutral description):
Input: "The USB drive has 64GB capacity and USB 3.0 interface."
Output: {{"sentiment": "neutral", "product": "usb drive", "issue": ""}}

Example 4 (Sarcastic/Negative):
Input: "Great quality! Broke after one week. Totally worth the money!"
Output: {{"sentiment": "negative", "product": "product", "issue": "broke after one week"}}

Now analyze this sentence:
Input: "{user_sentence}"
Output:"""


# ============================================================================
# API Calling Function
# ============================================================================

def call_responses_api(input_text, model="gpt-5"):
    """Call Responses API with GPT-5"""
    try:
        response = client.responses.create(
            model=model,
            input=input_text
        )
        return response.output_text
    except AttributeError as e:
        return f"ERROR: Your OpenAI SDK version doesn't support responses.create()"
    except Exception as e:
        return f"ERROR: {str(e)}"


# ============================================================================
# Scoring and Evaluation
# ============================================================================

def clean_json_output(text):
    """Extract JSON from text"""
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


def score_json(output_text, expected_sentiment=None):
    """Score output with optional expected sentiment check"""
    try:
        cleaned = clean_json_output(output_text)
        obj = json.loads(cleaned)
        
        required_keys = {"sentiment", "product", "issue"}
        keys_ok = set(obj.keys()) == required_keys
        
        valid_sentiments = {"positive", "neutral", "negative"}
        sentiment_ok = obj.get("sentiment", "").lower() in valid_sentiments
        
        product_ok = isinstance(obj.get("product"), str) and len(obj.get("product", "")) > 0
        issue_ok = "issue" in obj and isinstance(obj.get("issue"), str)
        
        # Check if sentiment matches expected (if provided)
        sentiment_match = True
        if expected_sentiment:
            sentiment_match = obj.get("sentiment", "").lower() == expected_sentiment.lower()
        
        if keys_ok and sentiment_ok and product_ok and issue_ok:
            return 1, obj, None, sentiment_match
        else:
            errors = []
            if not keys_ok: errors.append(f"wrong_keys: {set(obj.keys())}")
            if not sentiment_ok: errors.append(f"invalid_sentiment: {obj.get('sentiment')}")
            if not product_ok: errors.append("empty_or_invalid_product")
            if not issue_ok: errors.append("missing_or_invalid_issue")
            return 0, obj, ", ".join(errors), sentiment_match
            
    except json.JSONDecodeError as e:
        return 0, None, f"JSON parse error: {str(e)}", False
    except Exception as e:
        return 0, None, f"Unexpected error: {str(e)}", False


def eval_context(tag, input_builder, verbose=True):
    """Evaluate a context strategy"""
    if verbose:
        print(f"\n{'='*80}")
        print(f"  {tag}")
        print(f"{'='*80}\n")
    
    results = []
    total_score = 0
    sentiment_correct = 0
    
    for i, test_case in enumerate(TESTS, 1):
        test_text = test_case["text"]
        expected_sentiment = test_case.get("expected_sentiment")
        category = test_case.get("category", "")
        
        # Build input
        input_text = input_builder(test_text)
        
        # Call API
        output = call_responses_api(input_text)
        
        # Score output
        score, parsed, error, sentiment_match = score_json(output, expected_sentiment)
        total_score += score
        if sentiment_match:
            sentiment_correct += 1
        
        # Store result
        result = {
            "test_id": i,
            "category": category,
            "input": test_text[:80] + "..." if len(test_text) > 80 else test_text,
            "output": output,
            "parsed": parsed,
            "score": score,
            "error": error,
            "expected_sentiment": expected_sentiment,
            "sentiment_match": sentiment_match
        }
        results.append(result)
        
        # Print if verbose
        if verbose:
            print(f"Test {i} [{category}]:")
            print(f"Input: {test_text[:80]}{'...' if len(test_text) > 80 else ''}")
            print(f"Output: {output}")
            print(f"Parsed: {json.dumps(parsed, ensure_ascii=False) if parsed else 'FAILED'}")
            sentiment_indicator = "✓" if sentiment_match else f"✗ (expected: {expected_sentiment})"
            print(f"Score: {score}/1 {f'({error})' if error else '✓'} | Sentiment: {sentiment_indicator}")
            print()
    
    if verbose:
        print(f"[{tag}] Schema Score: {total_score}/{len(TESTS)}")
        print(f"[{tag}] Sentiment Accuracy: {sentiment_correct}/{len(TESTS)} ({sentiment_correct/len(TESTS)*100:.1f}%)")
        print(f"[{tag}] Combined Success Rate: {(total_score/len(TESTS)*0.5 + sentiment_correct/len(TESTS)*0.5)*100:.1f}%")
    
    return {
        "tag": tag,
        "total_score": total_score,
        "sentiment_correct": sentiment_correct,
        "max_score": len(TESTS),
        "schema_success_rate": total_score / len(TESTS),
        "sentiment_accuracy": sentiment_correct / len(TESTS),
        "combined_rate": (total_score / len(TESTS) * 0.5 + sentiment_correct / len(TESTS) * 0.5),
        "results": results
    }


def run_experiment():
    """Run the extended experiment"""
    print("\n" + "="*80)
    print("  EXTENDED CONTEXT ENGINEERING EXPERIMENT")
    print("  12 Challenging Test Cases")
    print("="*80)
    print(f"\n📊 Test Categories:")
    print("  - 2 Short reviews (positive & neutral)")
    print("  - 2 Pure positive reviews")
    print("  - 2 Pure neutral reviews")
    print("  - 1 Very long review (300+ words)")
    print("  - 3 Edge cases (no clear issue, multiple products, sarcasm)")
    print("  - 2 Tricky cases (disguised negative, extreme negative)\n")
    
    # Run all three contexts
    results_a = eval_context(
        "A: Baseline (minimal instruction)",
        build_context_a_input
    )
    
    if results_a is None:
        return
    
    results_b = eval_context(
        "B: Rules-based (strict format)",
        build_context_b_input
    )
    
    results_c = eval_context(
        "C: Few-shot (with diverse examples)",
        build_context_c_input
    )
    
    # Summary
    print("\n" + "="*80)
    print("  DETAILED COMPARISON")
    print("="*80 + "\n")
    
    print("Schema Correctness (JSON format valid):")
    for name, result in [("Context A", results_a), ("Context B", results_b), ("Context C", results_c)]:
        rate = result["schema_success_rate"]
        bar = "█" * int(rate * 30)
        print(f"{name:20s} {bar:30s} {rate*100:5.1f}% ({result['total_score']}/{result['max_score']})")
    
    print("\nSentiment Accuracy (matches expected sentiment):")
    for name, result in [("Context A", results_a), ("Context B", results_b), ("Context C", results_c)]:
        rate = result["sentiment_accuracy"]
        bar = "█" * int(rate * 30)
        print(f"{name:20s} {bar:30s} {rate*100:5.1f}% ({result['sentiment_correct']}/{result['max_score']})")
    
    print("\nCombined Success Rate (50% schema + 50% sentiment):")
    for name, result in [("Context A", results_a), ("Context B", results_b), ("Context C", results_c)]:
        rate = result["combined_rate"]
        bar = "█" * int(rate * 30)
        print(f"{name:20s} {bar:30s} {rate*100:5.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"experiment_results_extended_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "test_count": len(TESTS),
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
        
        print("\n" + "="*80)
        print("  KEY INSIGHTS")
        print("="*80)
        print("\nThis extended test set reveals:")
        print("  1. How well each context handles positive vs negative reviews")
        print("  2. Ability to detect sarcasm and disguised negativity")
        print("  3. Performance on edge cases (multiple products, no clear issue)")
        print("  4. Consistency across short and very long reviews")
        print("\n✨ Few-shot learning typically excels at nuanced sentiment detection!")
        
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
