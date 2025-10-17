"""
Extended Context Engineering Experiment
=======================================
包含 Rules-based, Few-shot, CoT (Chain-of-Thought), ReAct 的完整比較
plus 智能預判系統選擇最優策略
"""

import json
import os
import re
from datetime import datetime
from openai import OpenAI
from typing import Dict, List

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
    exit(1)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test sentences
TESTS = [
    "這支耳機音質不錯，但藍牙常常斷線。",
    "The keyboard feels great, but the battery dies too fast.",
    "相機畫質很棒，可是夜拍對焦很慢。",
    "我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，需要重新配對才能使用，這點真的很困擾。",
    "The mechanical keyboard I purchased has excellent build quality with a satisfying tactile feedback that makes typing a pleasure. However, I'm quite disappointed with the battery life - it only lasts about 3-4 days with the RGB lighting on, which is far shorter than the advertised 2 weeks. I find myself charging it constantly.",
    "這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。",
    "這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。"
]

# ============================================================================
# All Context Strategies
# ============================================================================

def build_rules_based_input(user_sentence):
    """Rules-based strategy"""
    return f"""Task: Extract fields from the sentence.
Return ONLY a JSON object with these exact keys: sentiment, product, issue.

Rules:
- sentiment must be one of: positive, neutral, negative
- If product is not explicit, infer the most likely product noun (e.g., 'headphones', 'keyboard')
- issue should describe the problem mentioned, or be empty string if none
- Return ONLY valid JSON, no comments, no extra text, no markdown code blocks
- Use lowercase English for all field values

Sentence: {user_sentence}"""

def build_few_shot_input(user_sentence):
    """Few-shot strategy"""
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

def build_cot_input(user_sentence):
    """Chain-of-Thought strategy"""
    return f"""You are a product review analyzer. Extract sentiment, product, and issue from reviews using step-by-step reasoning.

Task: Analyze the following review and extract sentiment, product, and issue.
Return your final answer as JSON with keys: sentiment, product, issue.

Let me think through this step by step:

1. **Identify the product**: First, I'll identify what product is being reviewed
2. **Analyze sentiment**: Then, I'll determine the overall sentiment by looking at positive/negative language
3. **Extract issues**: Finally, I'll identify any specific problems mentioned

Review to analyze: "{user_sentence}"

Let me work through this:

1. **Product identification**: Looking at the review, I need to identify what product is being discussed...

2. **Sentiment analysis**: I need to weigh the positive and negative aspects mentioned...

3. **Issue extraction**: I need to identify the specific problems mentioned...

Based on my step-by-step analysis, here is my final answer:"""

def build_react_input(user_sentence):
    """ReAct (Reasoning + Acting) strategy"""
    return f"""You are a product review analyzer using ReAct methodology. Use the format: Thought → Action → Observation → Thought → Action → Observation...

Task: Extract sentiment, product, and issue from this review: "{user_sentence}"

Let me use ReAct reasoning:

**Thought 1**: I need to analyze this review systematically. Let me start by identifying the product type.

**Action 1**: Examine the review for product-related keywords and context clues.

**Observation 1**: [Analyze the text for product indicators]

**Thought 2**: Now I should determine the overall sentiment by weighing positive vs negative expressions.

**Action 2**: Identify sentiment-bearing words and phrases, then evaluate the overall tone.

**Observation 2**: [Analyze sentiment indicators in the text]

**Thought 3**: Finally, I need to extract any specific issues or problems mentioned.

**Action 3**: Look for complaint words, problem descriptions, or negative experiences described.

**Observation 3**: [Identify specific issues mentioned]

**Thought 4**: Based on my systematic analysis, I can now provide the structured output.

**Final Answer**: Let me format this as the required JSON:"""

# ============================================================================
# Enhanced Strategy Predictor
# ============================================================================

class ExtendedStrategyPredictor:
    """擴展的策略預判器，支援4種策略選擇"""
    
    def __init__(self):
        self.complexity_weights = {
            'length': 0.15,
            'ambiguity': 0.25,
            'mixed_language': 0.15,
            'technical_terms': 0.15,
            'sentiment_clarity': 0.15,
            'reasoning_complexity': 0.15  # 新增：推理複雜度
        }
        
        # 不同複雜度模式對應的策略
        self.strategy_thresholds = {
            'rules_based': 0.3,     # 最簡單
            'few_shot': 0.5,        # 中等
            'cot': 0.7,             # 複雜推理
            'react': 0.8            # 最複雜
        }
        
        self.difficult_patterns = {
            'rules_based': [],  # 無特殊模式
            'few_shot': [
                r'但是.*不過.*還是',
                r'雖然.*可是.*然而', 
                r'整體.*(?:不過|但是|可是)',
            ],
            'cot': [
                r'一方面.*另一方面.*同時',    # 需要權衡多個因素
                r'原本.*後來.*現在',          # 時間序列分析
                r'表面上.*實際上.*總的來說',  # 深層vs表層分析
            ],
            'react': [
                r'說是.*但其實.*不過.*最後',  # 需要多步推理
                r'剛開始.*慢慢.*逐漸.*最終',  # 複雜的過程分析
                r'理論上.*實踐中.*經過.*發現', # 需要驗證和觀察
            ]
        }
    
    def analyze_reasoning_complexity(self, text: str) -> float:
        """分析推理複雜度"""
        # 因果關係詞
        causal_words = ['因為', '所以', '因此', 'because', 'therefore', 'thus']
        causal_count = sum(1 for word in causal_words if word in text)
        
        # 對比詞
        contrast_words = ['相比', '比較', 'compared', 'versus', 'against']  
        contrast_count = sum(1 for word in contrast_words if word in text)
        
        # 時間序列詞
        temporal_words = ['剛開始', '後來', '最後', '最終', 'initially', 'eventually', 'finally']
        temporal_count = sum(1 for word in temporal_words if word in text)
        
        reasoning_score = (causal_count + contrast_count + temporal_count) / 10
        return min(reasoning_score, 1.0)
    
    def analyze_input_complexity(self, text: str) -> Dict[str, float]:
        """擴展的複雜度分析"""
        features = {}
        
        features['length'] = min(len(text) / 200, 1.0)
        
        ambiguous_words = ['還好', '不錯', '一般', 'decent', 'okay', 'fine', '普通']
        ambiguity_count = sum(1 for word in ambiguous_words if word in text)
        features['ambiguity'] = min(ambiguity_count / 3, 1.0)
        
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        features['mixed_language'] = 0.3 if (has_chinese and has_english) else 0.0
        
        technical_patterns = [
            r'\w+(?:藍牙|WiFi|RGB|DPI|Hz|續航|韌體)', 
            r'(?:bluetooth|wireless|battery|firmware|latency|resolution)'
        ]
        tech_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                        for pattern in technical_patterns)
        features['technical_terms'] = min(tech_count / 5, 1.0)
        
        transition_words = ['但是', '不過', '可是', '然而', 'but', 'however', 'though', 'although']
        transition_count = sum(1 for word in transition_words if word in text)
        features['sentiment_clarity'] = min(transition_count / 2, 1.0)
        
        # 新增：推理複雜度
        features['reasoning_complexity'] = self.analyze_reasoning_complexity(text)
        
        return features
    
    def calculate_complexity_score(self, features: Dict[str, float]) -> float:
        score = sum(features[key] * self.complexity_weights[key] 
                   for key in features if key in self.complexity_weights)
        return min(score, 1.0)
    
    def detect_strategy_patterns(self, text: str) -> Dict[str, List[str]]:
        """檢測各策略的特定模式"""
        detected = {}
        for strategy, patterns in self.difficult_patterns.items():
            detected[strategy] = []
            for pattern in patterns:
                if re.search(pattern, text):
                    detected[strategy].append(pattern)
        return detected
    
    def predict_strategy(self, text: str) -> Dict:
        """預判最佳策略（4選1）"""
        features = self.analyze_input_complexity(text)
        complexity_score = self.calculate_complexity_score(features)
        pattern_matches = self.detect_strategy_patterns(text)
        
        # 檢查特定模式匹配
        for strategy in ['react', 'cot', 'few_shot']:  # 從最複雜開始檢查
            if pattern_matches[strategy]:
                return {
                    "strategy": strategy,
                    "reason": f"檢測到{strategy}模式: {pattern_matches[strategy][0]}",
                    "confidence": 0.85,
                    "complexity_score": complexity_score,
                    "features": features,
                    "detected_patterns": pattern_matches[strategy]
                }
        
        # 基於複雜度分數選擇
        if complexity_score >= self.strategy_thresholds['react']:
            strategy = "react"
            reason = f"極高複雜度 {complexity_score:.2f} >= {self.strategy_thresholds['react']}"
        elif complexity_score >= self.strategy_thresholds['cot']:
            strategy = "cot"
            reason = f"高複雜度 {complexity_score:.2f} >= {self.strategy_thresholds['cot']}"
        elif complexity_score >= self.strategy_thresholds['few_shot']:
            strategy = "few_shot"
            reason = f"中複雜度 {complexity_score:.2f} >= {self.strategy_thresholds['few_shot']}"
        else:
            strategy = "rules_based"
            reason = f"低複雜度 {complexity_score:.2f} < {self.strategy_thresholds['few_shot']}"
        
        confidence = min(max(complexity_score, 0.6), 0.95)
        
        return {
            "strategy": strategy,
            "reason": reason,
            "confidence": confidence,
            "complexity_score": complexity_score,
            "features": features,
            "detected_patterns": []
        }

# ============================================================================
# Token Usage Estimation
# ============================================================================

TOKEN_ESTIMATES = {
    'rules_based': 120,
    'few_shot': 250,
    'cot': 350,          # CoT需要更多推理文字
    'react': 450         # ReAct最複雜，token最多
}

# ============================================================================
# API and Evaluation Functions
# ============================================================================

def call_responses_api(input_text, model="gpt-5"):
    try:
        response = client.responses.create(
            model=model,
            input=input_text
        )
        return response.output_text
    except AttributeError as e:
        return f"ERROR: Your OpenAI SDK version doesn't support responses.create(). Please upgrade: pip install --upgrade openai"
    except Exception as e:
        return f"ERROR: {str(e)}"

def clean_json_output(text):
    # Clean CoT and ReAct reasoning text, keep only JSON
    if "Final Answer" in text:
        parts = text.split("Final Answer")
        text = parts[-1] if parts else text
    
    # Extract JSON from code blocks
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
    
    # Try to find JSON pattern
    json_match = re.search(r'\{[^{}]*"sentiment"[^{}]*\}', text)
    if json_match:
        text = json_match.group()
    
    return text.strip()

def score_json(output_text):
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

# ============================================================================
# Evaluation Functions
# ============================================================================

def evaluate_single_strategy(strategy_name, input_builder, verbose=True):
    """評估單一策略"""
    if verbose:
        print(f"\n{'='*70}")
        print(f"  {strategy_name.upper()}")
        print(f"{'='*70}\n")
    
    results = []
    total_score = 0
    total_tokens = 0
    
    for i, test_sentence in enumerate(TESTS, 1):
        input_text = input_builder(test_sentence)
        estimated_tokens = TOKEN_ESTIMATES.get(strategy_name.lower().replace('-', '_').replace(' ', '_'), 200)
        total_tokens += estimated_tokens
        
        output = call_responses_api(input_text)
        
        if output.startswith("ERROR: Your OpenAI SDK"):
            if verbose:
                print(f"\n⚠️  {output}")
            return None
        
        score, parsed, error = score_json(output)
        total_score += score
        
        result = {
            "test_id": i,
            "input": test_sentence,
            "output": output,
            "parsed": parsed,
            "score": score,
            "error": error,
            "estimated_tokens": estimated_tokens
        }
        results.append(result)
        
        if verbose:
            print(f"Test {i}: {test_sentence[:50]}{'...' if len(test_sentence) > 50 else ''}")
            print(f"Score: {score}/1 {f'({error})' if error else '✅'}")
            print()
    
    success_rate = total_score / len(TESTS)
    if verbose:
        print(f"Results: {total_score}/{len(TESTS)} ({success_rate*100:.1f}%)")
        print(f"Estimated tokens: ~{total_tokens}")
    
    return {
        "strategy": strategy_name,
        "total_score": total_score,
        "success_rate": success_rate,
        "total_tokens": total_tokens,
        "results": results
    }

def evaluate_smart_selection(predictor, verbose=True):
    """評估智能選擇策略"""
    if verbose:
        print(f"\n{'='*70}")
        print(f"  SMART STRATEGY SELECTION")
        print(f"{'='*70}\n")
    
    builders = {
        'rules_based': build_rules_based_input,
        'few_shot': build_few_shot_input,
        'cot': build_cot_input,
        'react': build_react_input
    }
    
    results = []
    total_score = 0
    total_tokens = 0
    strategy_counts = {strategy: 0 for strategy in builders.keys()}
    
    for i, test_sentence in enumerate(TESTS, 1):
        prediction = predictor.predict_strategy(test_sentence)
        selected_strategy = prediction["strategy"]
        strategy_counts[selected_strategy] += 1
        
        input_text = builders[selected_strategy](test_sentence)
        estimated_tokens = TOKEN_ESTIMATES.get(selected_strategy, 200)
        total_tokens += estimated_tokens
        
        output = call_responses_api(input_text)
        
        if output.startswith("ERROR: Your OpenAI SDK"):
            if verbose:
                print(f"\n⚠️  {output}")
            return None
        
        score, parsed, error = score_json(output)
        total_score += score
        
        result = {
            "test_id": i,
            "input": test_sentence,
            "prediction": prediction,
            "output": output,
            "parsed": parsed,
            "score": score,
            "error": error,
            "estimated_tokens": estimated_tokens
        }
        results.append(result)
        
        if verbose:
            print(f"Test {i}: {test_sentence[:50]}{'...' if len(test_sentence) > 50 else ''}")
            print(f"🎯 Selected: {selected_strategy} (confidence: {prediction['confidence']:.2f})")
            print(f"💡 Reason: {prediction['reason']}")
            print(f"Score: {score}/1 {f'({error})' if error else '✅'}")
            print()
    
    success_rate = total_score / len(TESTS)
    if verbose:
        print(f"{'='*70}")
        print(f"Results: {total_score}/{len(TESTS)} ({success_rate*100:.1f}%)")
        print(f"Strategy distribution:")
        for strategy, count in strategy_counts.items():
            print(f"  {strategy}: {count}/{len(TESTS)} ({count/len(TESTS)*100:.1f}%)")
        print(f"Total estimated tokens: ~{total_tokens}")
    
    return {
        "strategy": "Smart Selection",
        "total_score": total_score,
        "success_rate": success_rate,
        "total_tokens": total_tokens,
        "strategy_counts": strategy_counts,
        "results": results
    }

def run_extended_experiment():
    """運行擴展實驗"""
    print("\n" + "="*80)
    print("  EXTENDED CONTEXT ENGINEERING EXPERIMENT")
    print("  Rules-based | Few-shot | CoT | ReAct + Smart Selection")
    print("="*80)
    
    # 評估所有策略
    strategies_to_test = [
        ("Rules-based", build_rules_based_input),
        ("Few-shot", build_few_shot_input), 
        ("CoT (Chain-of-Thought)", build_cot_input),
        ("ReAct (Reasoning + Acting)", build_react_input)
    ]
    
    all_results = {}
    
    # 測試各個固定策略
    for strategy_name, builder in strategies_to_test:
        result = evaluate_single_strategy(strategy_name, builder)
        if result is None:
            return
        all_results[strategy_name] = result
    
    # 測試智能選擇
    predictor = ExtendedStrategyPredictor()
    smart_result = evaluate_smart_selection(predictor)
    if smart_result is None:
        return
    all_results["Smart Selection"] = smart_result
    
    # 比較結果
    print(f"\n{'='*80}")
    print("  COMPREHENSIVE COMPARISON")
    print("="*80)
    print(f"{'Strategy':<25} {'Success Rate':<12} {'Est. Tokens':<12} {'Efficiency':<10}")
    print("-" * 80)
    
    for strategy_name, result in all_results.items():
        efficiency = result["success_rate"] / (result["total_tokens"] / 1000)  # 成功率/千token
        print(f"{strategy_name:<25} {result['success_rate']*100:>8.1f}%    {result['total_tokens']:>8d}      {efficiency:>6.2f}")
    
    # 找出最佳策略
    best_by_accuracy = max(all_results.items(), key=lambda x: x[1]["success_rate"])
    best_by_efficiency = max(all_results.items(), key=lambda x: x[1]["success_rate"] / (x[1]["total_tokens"] / 1000))
    most_economical = min(all_results.items(), key=lambda x: x[1]["total_tokens"])
    
    print(f"\n🏆 Best by accuracy: {best_by_accuracy[0]} ({best_by_accuracy[1]['success_rate']*100:.1f}%)")
    print(f"⚡ Best efficiency: {best_by_efficiency[0]}")
    print(f"💰 Most economical: {most_economical[0]} (~{most_economical[1]['total_tokens']} tokens)")
    
    # 保存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"extended_context_experiment_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "experiment_type": "Extended Context Engineering with CoT, ReAct",
            "results": {k: v for k, v in all_results.items()},
            "summary": {
                "best_accuracy": best_by_accuracy[0],
                "best_efficiency": best_by_efficiency[0],
                "most_economical": most_economical[0]
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    try:
        run_extended_experiment()
        
        print("\n" + "="*80)
        print("  EXPERIMENT INSIGHTS")
        print("="*80)
        print("🧠 CoT: Best for complex reasoning tasks")
        print("🔄 ReAct: Best for multi-step analysis")
        print("📊 Few-shot: Reliable baseline with examples")
        print("📋 Rules-based: Most economical for simple tasks")
        print("🎯 Smart Selection: Optimal balance of all approaches")
        
    except Exception as e:
        print(f"\n❌ Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()