# 🚀 Quick Start Guide

## For First-Time Users

### 1. Get Your API Key
1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for a free account
3. Create a new API key
4. Copy the key (starts with `gsk_`)

### 2. Set Up the Project

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/multi-hop-rag-resume-screening.git
cd multi-hop-rag-resume-screening

# Install dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Edit .env and paste your API key
```

### 3. Run Your First Evaluation

```bash
# Set your API key (or add it to .env)
export GROQ_API_KEY='your_api_key_here'

# Run the pipeline
./run.sh
```

That's it! You should see candidate evaluations in your terminal.

## Understanding the Output

```
CANDIDATE #1: Jane Smith
✅ SCREENING RESULTS:
  • Overall Score: 0.90/1.0        ← High score = good match
  • Passed: ✓ YES                  ← Passed screening
  • Matching Skills: Python, AWS   ← Skills they have
  • Missing Skills: None            ← Skills they lack
```

## Adding Your Own Data

### Add Resumes

1. Place resume files in `resume/` folder
2. Supported formats: PDF, TXT
3. File naming: `firstname_lastname_resume.pdf`

```bash
resume/
├── alice_johnson.pdf
├── bob_smith.txt
└── carol_white.pdf
```

### Add Job Descriptions

1. Place job files in `job_description/` folder
2. Use descriptive filenames

```bash
job_description/
├── senior_engineer.txt
├── data_scientist.txt
└── frontend_developer.txt
```

### Run Again

```bash
python3 main.py
```

## Customization

### Change Screening Threshold

Edit `main.py`, line ~550:
```python
if screening['score'] < 0.5:  # Change 0.5 to your threshold
```

### Use Different LLM Model

Edit `main.py`, search for `llama-3.3-70b-versatile` and replace with:
- `llama-3.1-70b-versatile` (faster)
- `mixtral-8x7b-32768` (longer context)

### Adjust Number of Candidates

Edit `main.py`, line ~450:
```python
n_results=8  # Change to retrieve more/fewer candidates
```

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key error"
Make sure your `.env` file has:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

### "No candidates found"
- Check that resume files exist in `resume/` folder
- Verify files are readable (not corrupted)
- Try with the sample resumes first

## Next Steps

1. ⭐ Star the repository if you find it useful
2. 📖 Read the full [README.md](README.md)
3. 🤝 Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
4. 🐛 Report issues on [GitHub Issues](https://github.com/YOUR_USERNAME/multi-hop-rag-resume-screening/issues)

## Need Help?

- 📧 Open an issue on GitHub
- 💬 Start a discussion
- 📚 Read the documentation

---

Happy screening! 🎯
