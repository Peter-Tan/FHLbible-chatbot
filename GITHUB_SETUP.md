# GitHub Setup Guide 🚀

Complete guide to commit your code and open source it on GitHub.

## ⚠️ Before You Start

**IMPORTANT:** Make sure your `.env` file is NOT committed (it contains your API keys). It's already in `.gitignore`, but double-check:

```bash
# Verify .env is ignored
git status | grep .env
# Should show nothing (file is ignored)
```

## 📋 Step-by-Step Guide

### Step 1: Verify .gitignore

Check that sensitive files are ignored:

```bash
cat .gitignore
# Should include .env, logs/, .venv, etc.
```

### Step 2: Stage Your Files

```bash
# Add all files (except those in .gitignore)
git add .

# Verify what will be committed
git status
```

**Expected files to commit:**
- ✅ `src/` directory
- ✅ `README.md`
- ✅ `LICENSE`
- ✅ `pyproject.toml`
- ✅ `env.example`
- ✅ Documentation files (`.md` files)
- ✅ `.gitignore`
- ❌ `.env` (should NOT appear)
- ❌ `logs/` (should NOT appear)
- ❌ `.venv/` (should NOT appear)

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Bible Chatbot with Claude API integration

Features:
- Claude API integration for natural language Bible study
- FHL MCP Server integration with 19 Bible tools
- Parallel tool execution for performance
- Automatic conversation logging (JSON & text)
- History pruning for rate limit protection
- Complete documentation and code structure guides"
```

### Step 4: Create GitHub Repository

1. **Go to GitHub:**
   - Visit https://github.com/new
   - Or click "New repository" in your GitHub dashboard

2. **Repository Settings:**
   - **Repository name:** `bible-chatbot` (or your preferred name)
   - **Description:** `A conversational Bible study assistant powered by Claude API and FHL MCP Server`
   - **Visibility:** 
     - ✅ **Public** (for open source)
     - ⚠️ **Private** (if you want to keep it private first)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click **"Create repository"**

### Step 5: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/bible-chatbot.git

# Verify remote was added
git remote -v
```

### Step 6: Push to GitHub

```bash
# Push to GitHub (first time)
git branch -M main  # Rename branch to 'main' (GitHub standard)
git push -u origin main
```

If you're using `master` branch:

```bash
git push -u origin master
```

### Step 7: Verify on GitHub

1. Visit your repository: `https://github.com/YOUR_USERNAME/bible-chatbot`
2. Verify all files are there
3. Check that `.env` is NOT visible (it should be ignored)

## 🔄 Future Updates

For future changes:

```bash
# 1. Make your changes
# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "Description of your changes"

# 4. Push to GitHub
git push
```

## 📝 Good Commit Messages

Follow these guidelines:

```bash
# Good commit messages
git commit -m "Add parallel tool execution for performance"
git commit -m "Fix rate limit issue with history pruning"
git commit -m "Add conversation logging feature"
git commit -m "Update documentation with latest features"

# Avoid vague messages
git commit -m "fix"  # ❌ Too vague
git commit -m "update"  # ❌ Too vague
```

## 🏷️ Adding Tags (Optional)

For version releases:

```bash
# Create a tag
git tag -a v1.0.0 -m "Initial release: Bible Chatbot v1.0.0"

# Push tags to GitHub
git push origin v1.0.0
```

## 🔐 Security Checklist

Before pushing, verify:

- [ ] `.env` file is NOT in repository
- [ ] No API keys in code
- [ ] No passwords or secrets committed
- [ ] `.gitignore` includes sensitive files
- [ ] `env.example` has placeholder values only

## 📚 Repository Settings on GitHub

After pushing, configure:

1. **Add Topics/Tags:**
   - Go to repository → Settings → Topics
   - Add: `bible`, `chatbot`, `claude-api`, `mcp`, `python`, `bible-study`

2. **Add Description:**
   - Repository description: "A conversational Bible study assistant powered by Claude API and FHL MCP Server"

3. **Enable Issues:**
   - Settings → General → Features
   - Enable Issues and Discussions (for community)

4. **Add License:**
   - GitHub will auto-detect MIT license from LICENSE file

## 🌟 Making It Discoverable

1. **Add a good README** (already done ✅)
2. **Add topics/tags** (see above)
3. **Add screenshots** (optional, in README)
4. **Add badges** (optional, in README):
   ```markdown
   ![Python](https://img.shields.io/badge/python-3.10+-blue)
   ![License](https://img.shields.io/badge/license-MIT-green)
   ```

## 🔗 Adding FHL-MCP-Server as Submodule (Optional)

If you want to include FHL-MCP-Server as a git submodule:

```bash
# Remove existing FHL-MCP-Server if it's not a git repo
rm -rf FHL-MCP-Server

# Add as submodule
git submodule add https://github.com/ytssamuel/FHL-MCP-Server.git FHL-MCP-Server

# Commit the submodule
git commit -m "Add FHL-MCP-Server as submodule"
git push
```

**Note:** Users will need to clone with `--recursive`:
```bash
git clone --recursive https://github.com/YOUR_USERNAME/bible-chatbot.git
```

## 🐛 Troubleshooting

### "Permission denied" error
```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/bible-chatbot.git
```

### "Large files" error
```bash
# If FHL-MCP-Server is too large, add it to .gitignore
# and instruct users to clone it separately
echo "FHL-MCP-Server/" >> .gitignore
git add .gitignore
git commit -m "Exclude FHL-MCP-Server from repo (clone separately)"
```

### Already have a remote?
```bash
# Check existing remotes
git remote -v

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/bible-chatbot.git
```

## ✅ Final Checklist

Before making your repository public:

- [ ] All code committed
- [ ] `.env` file NOT in repository
- [ ] README.md is complete
- [ ] LICENSE file added
- [ ] `.gitignore` properly configured
- [ ] No sensitive data in code
- [ ] Repository pushed to GitHub
- [ ] Repository description added
- [ ] Topics/tags added
- [ ] Tested cloning the repository

## 🎉 You're Done!

Your code is now open source on GitHub! Share the repository URL with others.

**Next Steps:**
- Share on social media
- Add to your portfolio
- Write a blog post about it
- Submit to awesome lists
- Star your own repo! ⭐

---

**Repository URL:** `https://github.com/YOUR_USERNAME/bible-chatbot`

