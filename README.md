# Context Engineering Lab 🧪

A minimal viable experiment to validate how different **context engineering** approaches affect LLM output quality and consistency.

## 🎯 Experiment Overview

**Task**: Extract structured JSON from product reviews  
**Goal**: Compare three context engineering strategies (A/B/C testing)  
**Duration**: ~10-15 minutes  
**Model**: GPT-4o-mini (configurable)

### The Three Context Strategies

1. **Context A - Baseline** 📝
   - Minimal instruction
   - No format specification
   - No examples
   
2. **Context B - Rules-based** 📋
   - Strict output format
   - Explicit constraints
   - Schema definition
   
3. **Context C - Few-shot** 🎓
   - Rules from Context B
   - Plus 2 concrete examples
   - Input → Output pairs

## 🆕 New: Context Visualization Tools

**Visualize how your context evolves - like `git diff` for prompts!**

Track context changes, compare strategies, and measure real impact with our new visualization toolkit:

### ✨ Features

- 📊 **Context Diff** - See exactly what changed between versions
- 📈 **Evolution Timeline** - Track token usage and improvements
- 🔄 **Side-by-Side Comparison** - Visual comparison of contexts
- 🎯 **Response Quality Metrics** - Measure actual API performance
- 💾 **Export Results** - JSON export for analysis

### 🚀 Quick Demo

```bash
# Install visualization dependencies
pip install rich tiktoken

# Run demo (no API needed)
python context_visualizer.py

# Run live experiment (requires API key)
python context_visualizer_live.py
```

### 📚 Documentation

- 🎨 [5-Minute Quick Start](./QUICKSTART_VISUALIZATION.md) - Get started immediately
- 📖 [Complete Usage Guide](./VISUALIZATION_GUIDE.md) - All features explained
- 💡 [Concepts & Examples](./VISUALIZATION_SUMMARY.md) - Understanding context engineering

### 🎯 What You'll See

```
📈 Context Evolution Timeline

┌────────┬─────────────┬────────┬──────────┐
│ Step   │ Name        │ Tokens │ Δ Tokens │
├────────┼─────────────┼────────┼──────────┤
│ #0     │ Baseline    │     13 │          │
│ #1     │ + Rules     │     65 │      +52 │
│ #2     │ + Examples  │    161 │      +96 │
└────────┴─────────────┴────────┴──────────┘

🎯 Response Comparison

┌─────────────┬───────┬─────────────┐
│ Context     │ Score │ Result      │
├─────────────┼───────┼─────────────┤
│ Baseline    │   0%  │ ❌ Failed   │
│ + Rules     │ 100%  │ ✅ Perfect  │
│ + Examples  │ 100%  │ ✅ Perfect  │
└─────────────┴───────┴─────────────┘
```

**Real experiment results show Rules-based prompts achieve 100% accuracy vs 0% for baseline!**

---

## 🚀 Quick Start (Original Experiments)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Option A: Environment Variable (PowerShell)**
```powershell
$env:OPENAI_API_KEY='sk-your-key-here'
```

**Option B: Environment Variable (CMD)**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Option C: Create .env file**
```bash
# Copy the example and edit
copy .env.example .env
# Then edit .env with your actual API key
```

### 3. Run the Experiment

**Standard version:**
```bash
python context_experiment.py
```

**With .env support:**
```bash
python context_experiment_dotenv.py
```

**Responses API version (recommended):**
```bash
python context_experiment_responses_api.py
```

## 📊 What You'll See

The script will:

1. **Test each context** against 3 product reviews (mixed Chinese/English)
2. **Score outputs** based on:
   - Valid JSON parsing ✓
   - Correct keys present ✓
   - Valid sentiment values ✓
   - Non-empty product field ✓
   
3. **Generate comparison report**:
   ```
   Context A (Baseline)       ██████████          50.0%
   Context B (Rules)          ████████████████    80.0%
   Context C (Few-shot)       ████████████████████ 100.0%
   ```

4. **Save detailed results** to `experiment_results_TIMESTAMP.json`

## 🔍 Expected Findings

You should observe:

- ✅ **Baseline → Rules**: Format consistency improves
- ✅ **Rules → Few-shot**: Output reliability increases
- ✅ **Few-shot**: Highest success rate (often 100%)

This validates that **structured context** (rules + examples) produces more reliable, consistent outputs.

## 📁 Test Sentences

The experiment uses these 3 mixed-language product reviews:

1. 🎧 "這支耳機音質不錯，但藍牙常常斷線。" (Chinese)
2. ⌨️ "The keyboard feels great, but the battery dies too fast." (English)
3. 📷 "相機畫質很棒，可是夜拍對焦很慢。" (Chinese)

Expected output schema:
```json
{
  "sentiment": "positive|neutral|negative",
  "product": "product_name",
  "issue": "description_or_empty_string"
}
```

## 🎛️ Customization

### Change the Model

Edit `context_experiment.py`:
```python
def call_model(system_prompt, user_message, model="gpt-4o-mini"):
    # Change to: "gpt-4o", "gpt-4-turbo", etc.
```

### Add More Test Cases

Edit the `TESTS` list:
```python
TESTS = [
    "Your new test sentence 1",
    "Your new test sentence 2",
    # ...
]
```

### Adjust Temperature

Lower = more deterministic, Higher = more creative
```python
temperature=0.3  # Range: 0.0 - 2.0
```

## 📈 Next Steps

Want to extend this experiment? Try:

1. **🆕 Context Visualization** (Recommended!)
   - Use `context_visualizer.py` to see context evolution
   - Run `context_visualizer_live.py` for real API testing
   - Compare your custom prompts visually
   - See [QUICKSTART_VISUALIZATION.md](./QUICKSTART_VISUALIZATION.md)

2. **Prompt Injection Testing**
   - Add adversarial test cases
   - Test context robustness
   - Use visualization tools to debug failures
   
3. **Context Slicing**
   - Use longer reviews (500+ words)
   - Test summarization before extraction
   - Track token usage with visualization tools
   
4. **Observability**
   - Add Langfuse/PromptLayer integration
   - Combine with context visualization for complete tracking
   - Track token usage and latency
   
5. **LangGraph Version**
   - Convert A/B/C into state graph nodes
   - Add multi-strategy comparison logic
   - Visualize state transitions

## 📚 Learn More

- [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/chat)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🐛 Troubleshooting

### "OPENAI_API_KEY not set"
Make sure you've set the environment variable or created a `.env` file.

### "Insufficient quota"
Check your OpenAI account has available credits at [platform.openai.com/usage](https://platform.openai.com/usage)

### JSON parsing errors
The script automatically handles markdown code blocks. If issues persist, check the raw output in the JSON results file.

### Rate limits
Add a small delay between API calls if you hit rate limits:
```python
import time
time.sleep(1)  # After each API call
```

## 📄 License

MIT License - Feel free to use and modify for your own experiments!

## 🙋 Questions?

This is a minimal learning experiment. Feel free to:
- Modify the code
- Add your own test cases
- Experiment with different models
- Share your findings!

---

**Happy Context Engineering! 🚀**
