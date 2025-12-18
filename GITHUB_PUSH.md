# 📤 How to Push to GitHub

## Step 1: Configure Git (First Time Only)

```bash
cd /Users/saniyalahoti/.gemini/antigravity/scratch/capstone_resume_screening

# Set your name and email
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 2: Create GitHub Repository

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `multi-hop-rag-resume-screening` (or your choice)
3. Description: "Automated resume screening using Multi-Hop RAG and PEC agents"
4. Choose: **Public** (recommended) or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 3: Push Your Code

GitHub will show you commands. Use these:

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/saniyalahoti/multi-hop-rag-resume-screening.git
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

1. Go to your repository URL
2. You should see all files including:
   - ✅ README.md with badges
   - ✅ Sample resumes and job descriptions
   - ✅ Complete documentation
   - ✅ GitHub templates

## Step 5: Make It Look Professional

### Add Topics/Tags
On your GitHub repo page:
1. Click "⚙️ Settings" → "General"
2. Add topics: `rag`, `llm`, `resume-screening`, `ai`, `python`, `chromadb`, `groq`

### Update README
Replace `YOUR_USERNAME` in README.md with your actual GitHub username:
```bash
# Edit README.md
sed -i '' 's/YOUR_USERNAME/saniyalahoti/g' README.md

# Commit and push
git add README.md
git commit -m "Update: Replace placeholder username"
git push
```

### Add Repository Description
On GitHub:
1. Click "⚙️" next to "About"
2. Description: "Automated resume screening using Multi-Hop RAG and PEC agents"
3. Website: (optional)
4. Topics: `rag`, `llm`, `ai`, `python`, `resume-screening`

## Step 6: Share Your Project

Your repository URL will be:
```
https://github.com/YOUR_USERNAME/multi-hop-rag-resume-screening
```

Share it on:
- LinkedIn
- Twitter/X
- Reddit (r/MachineLearning, r/Python)
- Dev.to
- Your portfolio

## Future Updates

When you make changes:

```bash
# Make your changes to files
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: New feature description"

# Push to GitHub
git push
```

## Troubleshooting

### Authentication Error

If you get authentication errors, use a Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Copy the token
5. Use it as password when pushing

Or set up SSH keys (recommended):
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output and add to GitHub Settings → SSH Keys
```

### Already Exists Error

If repository already exists:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/NEW_REPO_NAME.git
git push -u origin main
```

## ✅ Checklist

Before pushing:
- [ ] Configured git name and email
- [ ] Created GitHub repository
- [ ] Updated README with your username
- [ ] Verified .env is in .gitignore (API key safety!)
- [ ] Tested the code locally
- [ ] All commits have clear messages

After pushing:
- [ ] Repository is visible on GitHub
- [ ] README displays correctly
- [ ] Added repository description and topics
- [ ] Shared with community (optional)

---

**Ready to push? Run the commands above!** 🚀
