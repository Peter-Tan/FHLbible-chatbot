#!/bin/bash
# Script to commit and push Bible Chatbot to GitHub

echo "🔍 Checking repository status..."

# Check if .env exists and is ignored
if git ls-files | grep -q ".env"; then
    echo "❌ ERROR: .env file is tracked! Remove it first:"
    echo "   git rm --cached .env"
    exit 1
else
    echo "✅ .env file is properly ignored"
fi

# Remove cache files from staging
echo "🧹 Cleaning up cache files..."
git rm --cached -r src/.cache/ 2>/dev/null || true

# Remove duplicate copy file if exists
if [ -f "src/chatbot拷貝.py" ]; then
    echo "🗑️  Removing duplicate file: src/chatbot拷貝.py"
    git rm --cached "src/chatbot拷貝.py" 2>/dev/null || true
fi

# Add all files
echo "📦 Staging files..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short

# Create commit
echo ""
echo "💾 Creating commit..."
git commit -m "Initial commit: Bible Chatbot with Claude API integration

Features:
- Claude API integration for natural language Bible study
- FHL MCP Server integration with 19 Bible tools
- Parallel tool execution for 2-5x performance improvement
- Automatic conversation logging (JSON & text formats)
- History pruning for rate limit protection
- Complete documentation and code structure guides
- Performance analysis and optimization guides"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    echo "   Branch: main"
    git push -u origin main
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "   Repository: $(git remote get-url origin)"
else
    echo ""
    echo "⚠️  No remote repository configured."
    echo "   Add remote with:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/bible-chatbot.git"
    echo "   Then run: git push -u origin main"
fi

