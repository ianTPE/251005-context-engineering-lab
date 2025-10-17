"""
Task Classification Framework
============================
區分開放性推理 vs 結構化任務，選擇最適合的prompt策略
"""

import re
from typing import Dict, List, Tuple
from enum import Enum

class TaskType(Enum):
    STRUCTURED_EXTRACTION = "structured_extraction"      # 結構化提取
    OPEN_REASONING = "open_reasoning"                    # 開放性推理
    ANALYTICAL_REASONING = "analytical_reasoning"        # 分析性推理
    CREATIVE_GENERATION = "creative_generation"          # 創意生成
    FACTUAL_QA = "factual_qa"                           # 事實問答
    PROBLEM_SOLVING = "problem_solving"                  # 問題解決

class TaskClassifier:
    """任務類型分類器"""
    
    def __init__(self):
        # 結構化任務的關鍵指標
        self.structured_indicators = {
            'output_format': [
                'JSON', 'json', 'CSV', 'xml', 'YAML', 'table', 'list',
                '表格', '清單', '格式', '欄位', '鍵值', 'key-value'
            ],
            'extraction_verbs': [
                'extract', 'parse', 'identify', 'classify', 'categorize',
                'label', 'tag', 'segment', 'detect',
                '提取', '解析', '識別', '分類', '標記', '檢測', '歸類'
            ],
            'fixed_schema': [
                'sentiment', 'product', 'issue', 'category', 'label',
                'score', 'rating', 'class', 'type', 'status',
                '情感', '產品', '問題', '類別', '評分', '狀態'
            ]
        }
        
        # 開放性推理的關鍵指標
        self.reasoning_indicators = {
            'reasoning_verbs': [
                'explain', 'analyze', 'discuss', 'evaluate', 'compare',
                'argue', 'justify', 'reason', 'conclude', 'infer',
                '解釋', '分析', '討論', '評估', '比較', '論證', '推理', '推斷'
            ],
            'open_questions': [
                'why', 'how', 'what if', 'suppose', 'consider',
                'explore', 'investigate', 'think about',
                '為什麼', '如何', '假如', '假設', '考慮', '探討', '思考'
            ],
            'creative_tasks': [
                'create', 'generate', 'design', 'invent', 'imagine',
                'brainstorm', 'propose', 'suggest',
                '創造', '生成', '設計', '發明', '想像', '建議', '提議'
            ]
        }
        
        # 最適策略映射
        self.strategy_mapping = {
            TaskType.STRUCTURED_EXTRACTION: ['rules_based', 'few_shot'],
            TaskType.OPEN_REASONING: ['cot', 'react'],
            TaskType.ANALYTICAL_REASONING: ['cot', 'react', 'few_shot'],
            TaskType.CREATIVE_GENERATION: ['react', 'cot'],
            TaskType.FACTUAL_QA: ['rules_based', 'few_shot'],
            TaskType.PROBLEM_SOLVING: ['react', 'cot']
        }

    def analyze_task_characteristics(self, prompt: str) -> Dict[str, float]:
        """分析任務特徵"""
        prompt_lower = prompt.lower()
        
        characteristics = {
            'has_fixed_format': 0.0,
            'extraction_focus': 0.0,
            'reasoning_complexity': 0.0,
            'creativity_required': 0.0,
            'open_ended_nature': 0.0,
            'structured_output': 0.0
        }
        
        # 檢測固定格式要求
        format_count = sum(1 for indicator in self.structured_indicators['output_format'] 
                          if indicator.lower() in prompt_lower)
        characteristics['has_fixed_format'] = min(format_count / 3, 1.0)
        
        # 檢測提取性動詞
        extract_count = sum(1 for verb in self.structured_indicators['extraction_verbs']
                           if verb.lower() in prompt_lower)
        characteristics['extraction_focus'] = min(extract_count / 3, 1.0)
        
        # 檢測推理性動詞
        reasoning_count = sum(1 for verb in self.reasoning_indicators['reasoning_verbs']
                             if verb.lower() in prompt_lower)
        characteristics['reasoning_complexity'] = min(reasoning_count / 3, 1.0)
        
        # 檢測創意性動詞
        creative_count = sum(1 for verb in self.reasoning_indicators['creative_tasks']
                            if verb.lower() in prompt_lower)
        characteristics['creativity_required'] = min(creative_count / 2, 1.0)
        
        # 檢測開放性問題
        open_count = sum(1 for question in self.reasoning_indicators['open_questions']
                        if question.lower() in prompt_lower)
        characteristics['open_ended_nature'] = min(open_count / 2, 1.0)
        
        # 檢測結構化輸出要求
        schema_count = sum(1 for field in self.structured_indicators['fixed_schema']
                          if field.lower() in prompt_lower)
        characteristics['structured_output'] = min(schema_count / 2, 1.0)
        
        return characteristics

    def classify_task(self, prompt: str) -> Tuple[TaskType, float, str]:
        """分類任務類型"""
        characteristics = self.analyze_task_characteristics(prompt)
        
        # 計算各類型的得分
        scores = {}
        
        # 結構化提取
        scores[TaskType.STRUCTURED_EXTRACTION] = (
            characteristics['has_fixed_format'] * 0.3 +
            characteristics['extraction_focus'] * 0.3 +
            characteristics['structured_output'] * 0.4
        )
        
        # 開放性推理
        scores[TaskType.OPEN_REASONING] = (
            characteristics['reasoning_complexity'] * 0.4 +
            characteristics['open_ended_nature'] * 0.6
        )
        
        # 分析性推理
        scores[TaskType.ANALYTICAL_REASONING] = (
            characteristics['reasoning_complexity'] * 0.5 +
            characteristics['structured_output'] * 0.3 +
            characteristics['extraction_focus'] * 0.2
        )
        
        # 創意生成
        scores[TaskType.CREATIVE_GENERATION] = (
            characteristics['creativity_required'] * 0.6 +
            characteristics['open_ended_nature'] * 0.4
        )
        
        # 事實問答 (有結構但不需複雜推理)
        scores[TaskType.FACTUAL_QA] = (
            characteristics['extraction_focus'] * 0.4 +
            (1 - characteristics['reasoning_complexity']) * 0.3 +
            (1 - characteristics['open_ended_nature']) * 0.3
        )
        
        # 問題解決
        scores[TaskType.PROBLEM_SOLVING] = (
            characteristics['reasoning_complexity'] * 0.4 +
            characteristics['open_ended_nature'] * 0.3 +
            characteristics['creativity_required'] * 0.3
        )
        
        # 找出最高分的任務類型
        best_task_type = max(scores.items(), key=lambda x: x[1])
        
        # 生成解釋
        explanation = self._generate_explanation(best_task_type[0], characteristics)
        
        return best_task_type[0], best_task_type[1], explanation

    def _generate_explanation(self, task_type: TaskType, characteristics: Dict[str, float]) -> str:
        """生成分類解釋"""
        explanations = {
            TaskType.STRUCTURED_EXTRACTION: f"結構化提取任務 - 固定格式: {characteristics['has_fixed_format']:.2f}, 結構化輸出: {characteristics['structured_output']:.2f}",
            TaskType.OPEN_REASONING: f"開放性推理任務 - 推理複雜度: {characteristics['reasoning_complexity']:.2f}, 開放性: {characteristics['open_ended_nature']:.2f}",
            TaskType.ANALYTICAL_REASONING: f"分析性推理任務 - 推理複雜度: {characteristics['reasoning_complexity']:.2f}, 結構化: {characteristics['structured_output']:.2f}",
            TaskType.CREATIVE_GENERATION: f"創意生成任務 - 創意需求: {characteristics['creativity_required']:.2f}, 開放性: {characteristics['open_ended_nature']:.2f}",
            TaskType.FACTUAL_QA: f"事實問答任務 - 提取導向: {characteristics['extraction_focus']:.2f}, 低推理需求",
            TaskType.PROBLEM_SOLVING: f"問題解決任務 - 推理複雜度: {characteristics['reasoning_complexity']:.2f}, 創意: {characteristics['creativity_required']:.2f}"
        }
        return explanations.get(task_type, "未知任務類型")

    def recommend_strategy(self, prompt: str) -> Dict[str, any]:
        """推薦最適策略"""
        task_type, confidence, explanation = self.classify_task(prompt)
        recommended_strategies = self.strategy_mapping.get(task_type, ['few_shot'])
        
        return {
            'task_type': task_type.value,
            'confidence': confidence,
            'explanation': explanation,
            'recommended_strategies': recommended_strategies,
            'primary_strategy': recommended_strategies[0] if recommended_strategies else 'few_shot'
        }

def demonstrate_task_classification():
    """演示任務分類"""
    classifier = TaskClassifier()
    
    # 測試案例
    test_prompts = [
        # 結構化提取
        "Extract sentiment, product, and issue from this review. Return as JSON.",
        "Parse the following text and classify it into categories.",
        
        # 開放性推理  
        "Why do you think this product failed in the market? Explain your reasoning.",
        "Analyze the implications of this business decision and discuss potential outcomes.",
        
        # 分析性推理
        "Compare these two approaches and evaluate which is more effective.",
        "Examine this data and provide insights with supporting evidence.",
        
        # 創意生成
        "Generate three creative marketing strategies for this product.",
        "Design an innovative solution to this problem.",
        
        # 事實問答
        "What is the capital of France?",
        "List the main features mentioned in this product description.",
        
        # 問題解決
        "How would you solve this technical issue step by step?",
        "Devise a plan to improve customer satisfaction based on these complaints."
    ]
    
    categories = [
        "結構化提取", "結構化提取",
        "開放性推理", "開放性推理", 
        "分析性推理", "分析性推理",
        "創意生成", "創意生成",
        "事實問答", "事實問答",
        "問題解決", "問題解決"
    ]
    
    print("=" * 80)
    print("  TASK CLASSIFICATION DEMONSTRATION")
    print("=" * 80)
    
    for i, (prompt, expected) in enumerate(zip(test_prompts, categories), 1):
        print(f"\n📝 Test {i}: {expected}")
        print("-" * 70)
        print(f"Prompt: {prompt}")
        
        recommendation = classifier.recommend_strategy(prompt)
        
        print(f"🎯 Classified as: {recommendation['task_type']}")
        print(f"📊 Confidence: {recommendation['confidence']:.2f}")
        print(f"💡 Explanation: {recommendation['explanation']}")
        print(f"🚀 Recommended strategies: {recommendation['recommended_strategies']}")
        print(f"⭐ Primary strategy: {recommendation['primary_strategy']}")

def create_improved_strategy_predictor():
    """創建改進的策略預判器"""
    print("""
🔧 **改進的策略選擇系統**：

```python
class ImprovedStrategyPredictor:
    def __init__(self):
        self.task_classifier = TaskClassifier()
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def predict_optimal_strategy(self, prompt, user_input=""):
        # 1. 分析任務類型
        task_recommendation = self.task_classifier.recommend_strategy(prompt)
        
        # 2. 分析輸入複雜度  
        complexity_score = self.complexity_analyzer.analyze(user_input)
        
        # 3. 綜合決策
        if task_recommendation['task_type'] == 'structured_extraction':
            if complexity_score < 0.3:
                return 'rules_based'
            else:
                return 'few_shot'
        
        elif task_recommendation['task_type'] == 'open_reasoning':
            if complexity_score < 0.5:
                return 'cot'
            else:
                return 'react'
        
        # 4. 其他類型的邏輯...
        return task_recommendation['primary_strategy']
```

**關鍵改進**：
1. 🎯 任務類型導向的策略選擇
2. 📊 複雜度分析作為輔助判斷
3. 🔄 動態適應不同任務需求
4. ✅ 避免策略與任務類型不匹配
""")

if __name__ == "__main__":
    demonstrate_task_classification()
    create_improved_strategy_predictor()
    
    print("""
✅ **總結 - 如何區分開放性推理 vs 結構化任務**：

📋 **結構化任務特徵**：
- 明確的輸出格式要求 (JSON, CSV, 表格等)
- 提取性動詞 (extract, parse, identify)
- 固定的schema或欄位
- 分類、標記、檢測類任務
- ➡️ 適合: Rules-based, Few-shot

🧠 **開放性推理特徵**：
- 推理性動詞 (explain, analyze, discuss)
- 開放性問題 (why, how, what if)
- 需要論證、評估、比較
- 多角度思考、創意發想
- ➡️ 適合: CoT, ReAct

🎯 **關鍵判斷標準**：
1. 輸出是否有固定格式？
2. 是否需要複雜推理過程？
3. 答案是否有標準答案？
4. 是否需要創意或多角度思考？
""")