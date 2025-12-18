#!/bin/bash

# Multi-Hop RAG Resume Screening - Run Script
# This script sets up the environment and runs the pipeline

echo "🚀 Multi-Hop RAG Resume Screening Pipeline"
echo "=========================================="
echo ""

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set!"
    echo ""
    echo "Please set your Groq API key:"
    echo "  export GROQ_API_KEY='your-api-key-here'"
    echo ""
    echo "Get a free API key at: https://console.groq.com/keys"
    exit 1
fi

echo "✓ API key found"
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import chromadb, pypdf, sentence_transformers, groq" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "✓ All dependencies found"
fi

echo ""
echo "🏃 Running pipeline..."
echo ""

# Run the main script
python3 main.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Pipeline completed successfully!"
else
    echo ""
    echo "❌ Pipeline failed. Check logs above for details."
    exit 1
fi
