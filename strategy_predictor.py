"""
Strategy Predictor: 智能預判系統
================================
基於輸入特徵預判是否使用 rules-based 或 few-shot，
避免浪費token在不必要的few-shot上
"""

import re
import json
from typing import Dict, List, Tuple

class StrategyPredictor:
    """預判要使用哪種prompt策略的智能系統"""
    
    def __init__(self):
        # 基於經驗的權重（可以用機器學習優化）
        self.complexity_weights = {
            'length': 0.2,
            'ambiguity': 0.3,
            'mixed_language': 0.2,
            'technical_terms': 0.15,
            'sentiment_clarity': 0.15
        }
        
        # 已知困難模式（可動態更新）
        self.known_difficult_patterns = [
            r'但是.*不過.*還是',  # 複雜轉折
            r'雖然.*可是.*然而',  # 多層轉折
            r'一方面.*另一方面',  # 對比描述
            r'整體.*(?:不過|但是|可是)',  # 整體vs局部評價
        ]
    
    def analyze_input_complexity(self, text: str) -> Dict[str, float]:
        """分析輸入文本的複雜度特徵"""
        features = {}
        
        # 1. 長度複雜度 (0-1)
        features['length'] = min(len(text) / 200, 1.0)
        
        # 2. 語言歧義度 (檢測模糊詞彙)
        ambiguous_words = ['還好', '不錯', '一般', 'decent', 'okay', 'fine', '普通']
        ambiguity_count = sum(1 for word in ambiguous_words if word in text)
        features['ambiguity'] = min(ambiguity_count / 3, 1.0)
        
        # 3. 混合語言複雜度
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        features['mixed_language'] = 0.3 if (has_chinese and has_english) else 0.0
        
        # 4. 技術術語密度
        technical_patterns = [
            r'\w+(?:藍牙|WiFi|RGB|DPI|Hz|續航|韌體)', 
            r'(?:bluetooth|wireless|battery|firmware|latency|resolution)'
        ]
        tech_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                        for pattern in technical_patterns)
        features['technical_terms'] = min(tech_count / 5, 1.0)
        
        # 5. 情感表達清晰度 (轉折詞越多越複雜)
        transition_words = ['但是', '不過', '可是', '然而', 'but', 'however', 'though', 'although']
        transition_count = sum(1 for word in transition_words if word in text)
        features['sentiment_clarity'] = min(transition_count / 2, 1.0)
        
        return features
    
    def calculate_complexity_score(self, features: Dict[str, float]) -> float:
        """計算總體複雜度分數 (0-1)"""
        score = sum(features[key] * self.complexity_weights[key] 
                   for key in features if key in self.complexity_weights)
        return min(score, 1.0)
    
    def detect_known_patterns(self, text: str) -> List[str]:
        """檢測已知的困難模式"""
        detected = []
        for pattern in self.known_difficult_patterns:
            if re.search(pattern, text):
                detected.append(pattern)
        return detected
    
    def predict_strategy(self, text: str, threshold: float = 0.4) -> Dict:
        """
        預判最佳策略
        
        Args:
            text: 輸入文本
            threshold: 複雜度門檻，超過則使用few-shot
        
        Returns:
            預測結果字典
        """
        # 分析特徵
        features = self.analyze_input_complexity(text)
        complexity_score = self.calculate_complexity_score(features)
        difficult_patterns = self.detect_known_patterns(text)
        
        # 決策邏輯
        if difficult_patterns:
            strategy = "few_shot"
            reason = f"檢測到困難模式: {', '.join(difficult_patterns[:2])}"
            confidence = 0.8
        elif complexity_score > threshold:
            strategy = "few_shot"
            reason = f"複雜度分數 {complexity_score:.2f} > 門檻 {threshold}"
            confidence = min(complexity_score * 1.2, 1.0)
        else:
            strategy = "rules_based"
            reason = f"複雜度分數 {complexity_score:.2f} <= 門檻 {threshold}"
            confidence = max(1.0 - complexity_score, 0.6)
        
        return {
            "strategy": strategy,
            "reason": reason,
            "confidence": confidence,
            "complexity_score": complexity_score,
            "features": features,
            "difficult_patterns": difficult_patterns
        }

def create_adaptive_system():
    """創建自適應策略選擇系統"""
    print("""
🤖 **自適應策略選擇系統**：

```python
class AdaptivePromptSystem:
    def __init__(self):
        self.predictor = StrategyPredictor()
        self.success_history = {}  # 記錄成功率
        
    def process_request(self, text, cost_priority="medium"):
        # 1. 預判策略
        prediction = self.predictor.predict_strategy(text)
        
        # 2. 根據成本優先級調整
        if cost_priority == "high" and prediction["confidence"] < 0.9:
            strategy = "rules_based"  # 強制省錢
        else:
            strategy = prediction["strategy"]
        
        # 3. 執行並記錄結果
        result = self.execute_with_strategy(text, strategy)
        self.update_history(text, strategy, result["success"])
        
        return result
    
    def update_history(self, text, strategy, success):
        # 更新成功率統計，用於改進預判
        pass
```
""")

def demonstrate_predictor():
    """演示預判系統"""
    predictor = StrategyPredictor()
    
    # 測試案例
    test_cases = [
        "Good product",  # 簡單 -> rules-based
        "這支耳機音質不錯，但藍牙常常斷線。",  # 中等 -> rules-based
        "整體來說音質表現相當出色，不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯",  # 複雜 -> few-shot
        "雖然build quality很好，但是battery life讓人失望，不過RGB效果還是很讚的",  # 混合語言+複雜轉折 -> few-shot
    ]
    
    print("=" * 80)
    print("  STRATEGY PREDICTION DEMO")
    print("=" * 80)
    
    total_tokens_saved = 0
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {text[:60]}{'...' if len(text) > 60 else ''}")
        print("-" * 70)
        
        prediction = predictor.predict_strategy(text)
        
        print(f"🎯 Predicted Strategy: {prediction['strategy']}")
        print(f"💡 Reason: {prediction['reason']}")
        print(f"📊 Confidence: {prediction['confidence']:.2f}")
        print(f"🔧 Complexity Score: {prediction['complexity_score']:.3f}")
        
        if prediction['difficult_patterns']:
            print(f"⚠️  Difficult Patterns: {prediction['difficult_patterns']}")
        
        # 估算token節省
        if prediction['strategy'] == 'rules_based':
            tokens_saved = 128  # 平均節省的token數
            total_tokens_saved += tokens_saved
            print(f"💰 Estimated tokens saved: ~{tokens_saved}")
    
    print(f"\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Total estimated tokens saved: ~{total_tokens_saved}")
    print(f"Equivalent cost savings: ~${total_tokens_saved * 0.00003:.4f}")

def create_integration_example():
    """展示如何整合到現有系統"""
    print("""
🔧 **整合到現有系統的範例**：

```python
# 在原本的context_experiment程式中：

def smart_eval_context(tag, input_builder, predictor, verbose=True):
    results = []
    tokens_saved = 0
    
    for test_sentence in TESTS:
        # 🚀 關鍵改進：預判策略
        prediction = predictor.predict_strategy(test_sentence)
        
        if prediction["strategy"] == "rules_based":
            # 使用省錢策略
            input_text = build_context_b_input(test_sentence)
            tokens_saved += 128  # 估算節省
        else:
            # 使用穩定策略
            input_text = build_context_c_input(test_sentence)
        
        # 執行API調用
        output = call_responses_api(input_text)
        score, parsed, error = score_json(output)
        
        # 記錄結果
        results.append({
            "prediction": prediction,
            "tokens_saved": tokens_saved,
            "score": score
        })
        
        if verbose:
            print(f"Strategy: {prediction['strategy']} (confidence: {prediction['confidence']:.2f})")
            print(f"Score: {score}/1")
    
    print(f"Total tokens saved: {tokens_saved}")
    return results

# 使用方式：
predictor = StrategyPredictor()
results = smart_eval_context("Smart Adaptive", None, predictor)
```
""")

if __name__ == "__main__":
    print("🎯 Strategy Predictor - 智能預判系統")
    demonstrate_predictor()
    create_adaptive_system()
    create_integration_example()
    
    print("""
✅ **核心優勢**：
1. 🚀 事前預判，無需浪費token測試
2. 💰 自動選擇最經濟的策略
3. 🎯 基於文本特徵的智能決策
4. 📈 可學習優化的系統設計
5. ⚡ 即時決策，無延遲
""")