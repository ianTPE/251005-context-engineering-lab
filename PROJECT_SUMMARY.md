# 📋 Project Summary

## Context Engineering Lab - What We Built

This project is a **minimal viable experiment** to validate how different context engineering approaches affect LLM output quality. Perfect for learning and experimentation!

---

## 📦 Complete File Structure

```
251005-context-engineering-lab/
├── context_experiment.py           # Main experiment script
├── context_experiment_dotenv.py    # Enhanced version with .env support
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
├── .gitignore                      # Protects sensitive files
├── README.md                       # Full documentation
├── QUICKSTART.md                   # 3-minute setup guide
└── PROJECT_SUMMARY.md              # This file
```

---

## 🎯 What This Experiment Does

### The Task
Extract structured JSON from product reviews:
```json
{
  "sentiment": "positive|neutral|negative",
  "product": "product_name",
  "issue": "description_or_empty"
}
```

### The Test Cases (3 sentences)
1. 🎧 "這支耳機音質不錯,但藍牙常常斷線。" (Chinese)
2. ⌨️ "The keyboard feels great, but the battery dies too fast." (English)
3. 📷 "相機畫質很棒,可是夜拍對焦很慢。" (Chinese)

### The Three Context Strategies (A/B/C Testing)

| Context | Description | What's Included |
|---------|-------------|-----------------|
| **A: Baseline** | Minimal instruction | Just task description |
| **B: Rules-based** | Strict format + constraints | JSON schema, validation rules |
| **C: Few-shot** | Rules + examples | Context B + 2 example pairs |

---

## 🔬 What You Learn

By running this experiment, you'll discover:

1. **Format Consistency**: How rules improve output structure
2. **Reliability**: How few-shot examples reduce errors
3. **Quantitative Validation**: Actual success rate percentages
4. **Practical Patterns**: Real-world context engineering techniques

Expected results pattern:
```
Context A (Baseline)    ██████████          50-60%
Context B (Rules)       ████████████████    70-85%
Context C (Few-shot)    ████████████████████ 90-100%
```

---

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **API**: OpenAI Chat Completions (gpt-4o-mini default)
- **Dependencies**: 
  - `openai>=1.0.0` - Official OpenAI SDK
  - `python-dotenv>=1.0.0` - Environment variable management

---

## 📝 Key Features

### Automatic Scoring System
- ✅ Valid JSON parsing
- ✅ Correct keys present
- ✅ Valid sentiment values
- ✅ Non-empty required fields

### Output Format
- Console display with visual progress
- JSON file with full results
- Success rate comparison chart
- Timestamp-based result files

### Developer Experience
- Clear error messages
- API key validation
- Multiple setup options
- .env support

---

## 🚀 How to Use

### Quick Start (3 steps)
```powershell
# 1. Install
pip install -r requirements.txt

# 2. Set API key
$env:OPENAI_API_KEY='your-key-here'

# 3. Run
python context_experiment.py
```

See **QUICKSTART.md** for detailed instructions.

---

## 🎓 Educational Value

This project teaches:

1. **Context Engineering Fundamentals**
   - Baseline vs. structured prompts
   - Rule-based constraints
   - Few-shot learning patterns

2. **Prompt Evaluation Methodology**
   - Quantitative scoring
   - A/B/C testing approach
   - Reproducible experiments

3. **Best Practices**
   - API key management
   - Error handling
   - Result persistence
   - Git security (.gitignore)

---

## 📈 Extension Ideas

Ready to go deeper? Try these:

### Level 1: Basic Extensions
- Add more test sentences (different languages/products)
- Change the model (gpt-4o, claude-3.5-sonnet)
- Adjust temperature (test consistency)

### Level 2: Advanced Features
- **Prompt injection testing**: Test robustness
- **Context slicing**: Handle longer texts
- **Multi-model comparison**: Compare different LLMs

### Level 3: Production-Ready
- **Observability**: Add Langfuse/LangSmith
- **LangGraph version**: Convert to state graph
- **Batch processing**: Test 100+ samples
- **Cost tracking**: Monitor token usage

---

## 🔐 Security Notes

This project follows best practices:

- ✅ API keys never hardcoded
- ✅ .env files in .gitignore
- ✅ Clear setup instructions
- ✅ Example files for reference

**Remember**: Never commit your actual `.env` file!

---

## 📊 Success Metrics

After running the experiment, you should see:

1. **Quantified Improvement**: B > A, C > B
2. **High Reliability**: Context C often reaches 100%
3. **Clear Patterns**: Consistent failure modes in A/B
4. **Actionable Insights**: What makes prompts better

---

## 🤝 Contributing

This is a learning project! Feel free to:
- Modify the code for your use case
- Add new context strategies
- Test different scoring criteria
- Share your findings

---

## 📚 Resources

- [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/chat)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangChain/LangGraph Docs](https://python.langchain.com/)

---

## ✨ What Makes This Special?

1. **Minimal but Complete**: ~250 lines, full experiment
2. **Real-World Task**: Practical sentiment extraction
3. **Quantitative**: Actual numbers, not just vibes
4. **Reproducible**: Same setup, same results
5. **Educational**: Learn by doing

---

## 🎯 Next Steps

1. ✅ Run the experiment: `python context_experiment.py`
2. 📊 Review the results JSON file
3. 🔬 Try modifying one context version
4. 📈 Compare your results
5. 🚀 Build your own experiment!

---

**Built with ❤️ for learning Context Engineering**

*Duration to complete: ~10-15 minutes*  
*Complexity: Beginner-friendly*  
*Learning value: High* 🌟
