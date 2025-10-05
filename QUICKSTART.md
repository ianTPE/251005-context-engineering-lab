# 🚀 Quick Start Guide

Get your Context Engineering experiment running in 3 minutes!

## Step 1: Install Dependencies (1 min)

```powershell
pip install -r requirements.txt
```

Expected output: `Successfully installed openai-2.x.x python-dotenv-1.x.x ...`

## Step 2: Set API Key (1 min)

### Option A: Environment Variable (Quick)

**PowerShell:**
```powershell
$env:OPENAI_API_KEY='sk-your-actual-api-key-here'
```

**CMD:**
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Option B: .env File (Persistent)

1. Copy the example file:
   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` with your favorite editor:
   ```powershell
   notepad .env
   ```

3. Replace `your-api-key-here` with your actual OpenAI API key

4. Run the enhanced version:
   ```powershell
   python context_experiment_dotenv.py
   ```

## Step 3: Run the Experiment (1 min)

```powershell
python context_experiment.py
```

## What You'll See

```
============================================================
  CONTEXT ENGINEERING EXPERIMENT
  Task: Extract structured sentiment from product reviews
============================================================

============================================================
  A: Baseline (minimal instruction)
============================================================

Test 1: 這支耳機音質不錯,但藍牙常常斷線。
Output: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth disconnection"}
Parsed: {"sentiment": "negative", "product": "headphones", "issue": "bluetooth disconnection"}
Score: 1/1 ✓

[... more tests ...]

============================================================
  SUMMARY COMPARISON
============================================================

Context A (Baseline)       ██████████          50.0%
Context B (Rules)          ████████████████    80.0%
Context C (Few-shot)       ████████████████████ 100.0%

📊 Detailed results saved to: experiment_results_20250525_180500.json
```

## Files Created

- **context_experiment.py** - Main experiment script
- **context_experiment_dotenv.py** - Enhanced version with .env support
- **requirements.txt** - Python dependencies
- **README.md** - Full documentation
- **.env.example** - Environment template
- **.gitignore** - Protects sensitive files

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you ran one of the commands in Step 2
- Verify your API key is correct (starts with `sk-`)

### "Insufficient quota"
- Check your OpenAI usage: https://platform.openai.com/usage
- Verify your account has credits

### Import errors
- Make sure you ran `pip install -r requirements.txt`
- Try: `python -m pip install --upgrade openai`

## Next Steps

✅ Experiment completed? Try these extensions:

1. **Add more test cases** - Edit `TESTS` list in the script
2. **Try different models** - Change `model="gpt-4o"` 
3. **Test with longer text** - Add 500+ word reviews
4. **Add adversarial tests** - Test prompt injection resistance

## Need Help?

Check the full **README.md** for:
- Detailed explanation of each context strategy
- How to customize the experiment
- Advanced extensions (LangGraph, observability)
- Troubleshooting guide

---

**Ready to learn? Run the experiment now! 🎯**
