# Contributing to Multi-Hop RAG Resume Screening

Thank you for your interest in contributing! 🎉

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/multi-hop-rag-resume-screening.git
   cd multi-hop-rag-resume-screening
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Set up environment
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

## 🧪 Testing

Before submitting a PR, ensure all tests pass:

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Check code style
black --check main.py
flake8 main.py
```

## 📝 Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://github.com/psf/black) for code formatting
- Add docstrings to all functions and classes
- Keep functions focused and under 50 lines when possible

Example:
```python
def process_resume(resume_path: str) -> dict:
    """
    Process a resume file and extract relevant information.
    
    Args:
        resume_path: Path to the resume file (PDF or TXT)
        
    Returns:
        Dictionary containing extracted resume data
        
    Raises:
        FileNotFoundError: If resume file doesn't exist
    """
    # Implementation here
    pass
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

## ✨ Suggesting Features

We welcome feature suggestions! Please:

- Check existing issues first
- Provide a clear use case
- Explain why this feature would be useful
- Include examples if possible

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

## 📥 Submitting Pull Requests

1. **Update your fork** with the latest changes:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Make your changes** in your feature branch

3. **Test thoroughly**:
   ```bash
   pytest tests/
   black main.py
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add: Feature description"
   ```
   
   Use prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements
   - `Docs:` for documentation
   - `Refactor:` for code restructuring

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## 📋 PR Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No API keys or secrets in code
- [ ] `.gitignore` is respected

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **Testing**: Add unit tests and integration tests
- **Documentation**: Improve README, add tutorials
- **Features**: Implement roadmap items
- **Performance**: Optimize processing speed
- **Bug Fixes**: Fix reported issues
- **Examples**: Add more sample resumes/jobs

## 🤔 Questions?

- Open a [discussion](https://github.com/SaniyaLahoti/Capstone_project/discussions)
- Check existing issues and PRs
- Reach out to maintainers

## 📜 Code of Conduct

Please be respectful and constructive. We're all here to learn and improve!

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

Happy coding! 🚀
