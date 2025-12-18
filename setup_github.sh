#!/bin/bash

# GitHub Setup Script
# This script initializes a git repository and prepares it for GitHub

echo "🚀 GitHub Setup for Multi-Hop RAG Resume Screening"
echo "=================================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Initialize git repository if not already initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

echo ""

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY before committing!"
else
    echo "✓ .env file already exists"
fi

echo ""

# Add all files to git
echo "📋 Staging files..."
git add .

# Show status
echo ""
echo "📊 Git status:"
git status

echo ""
echo "📝 Ready to commit! Next steps:"
echo ""
echo "1. Review the staged files above"
echo "2. Commit your changes:"
echo "   git commit -m 'Initial commit: Multi-Hop RAG Resume Screening'"
echo ""
echo "3. Create a new repository on GitHub"
echo "   https://github.com/new"
echo ""
echo "4. Add remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "✅ Setup complete!"
