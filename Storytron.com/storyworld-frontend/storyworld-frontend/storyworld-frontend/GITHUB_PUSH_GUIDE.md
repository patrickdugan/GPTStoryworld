# GitHub Push Guide

Quick guide to push this frontend to your GPTStoryworld repository.

## Option 1: Add to Existing Repo

```bash
# Navigate to your existing GPTStoryworld repo
cd ~/GPTStoryworld

# Create a frontend directory
mkdir frontend
cd frontend

# Copy all frontend files here
# (or extract the gpt-storyworld-frontend.tar.gz)

# Add to git
git add .
git commit -m "Add React frontend UI for storyworld generation

- Interactive sliders for parameters (characters, themes, variables, length)
- Direct GPT-4 API integration
- System prompt preview and customization
- API key management modal
- JSON export functionality
- Responsive design with gradient UI
- Complete documentation (README, INTEGRATION, DEPLOYMENT)"

git push origin main
```

## Option 2: Create New Frontend Repo

```bash
# Navigate to the frontend folder
cd storyworld-frontend

# Initialize git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: GPT Storyworld Frontend

Interactive React UI for generating Sweepweave-compatible storyworlds
with visual parameter configuration and direct GPT API integration."

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/patrickdugan/GPTStoryworld-Frontend.git

# Push
git branch -M main
git push -u origin main
```

## Option 3: Separate Branch in Main Repo

```bash
cd ~/GPTStoryworld

# Create and switch to new branch
git checkout -b frontend-ui

# Copy frontend files to root or subfolder
cp -r ~/storyworld-frontend/* ./frontend/

# Commit
git add .
git commit -m "Add interactive frontend UI"

# Push branch
git push origin frontend-ui

# Then create a Pull Request on GitHub
```

## Recommended Repo Structure

```
GPTStoryworld/
├── README.md                 # Main repo readme
├── package.json              # CLI package config
├── index.js                  # CLI entry point
├── raw_storyworld.json       # CLI data
├── meta.json                 # Metadata tracker
├── encounters/               # Generated encounters
├── frontend/                 # ← New frontend folder
│   ├── README.md
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── INTEGRATION.md
│   ├── DEPLOYMENT.md
│   └── demo.html
└── .gitignore
```

## Update Main README

Add a section to your main `README.md`:

```markdown
## 🎨 Frontend UI

A beautiful React-based web interface is now available! 

### Features
- Visual parameter configuration with sliders
- Direct GPT-4 API integration
- System prompt preview
- Secure API key management
- One-click JSON export

### Quick Start
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

See [frontend/README.md](frontend/README.md) for complete documentation.

### Live Demo
Try the [interactive demo](frontend/demo.html) (open in browser)
```

## GitHub Repository Settings

### Topics (for discoverability)
Add these topics to your repo:

```
gpt-4
storyworld
narrative-ai
react
openai-api
game-development
interactive-fiction
typescript
```

### About Section
```
Meta-GPT API prompter for Sweepweave Storyworlds with React frontend
```

### Repository Structure
- ✅ Add detailed README
- ✅ Include LICENSE (MIT recommended)
- ✅ Add .gitignore for node_modules
- ✅ Create releases for versions
- ✅ Enable GitHub Pages for demo

## Create a Release

```bash
# Tag the version
git tag -a v1.0.0 -m "Frontend UI v1.0.0 - Initial release"
git push origin v1.0.0
```

Then on GitHub:
1. Go to Releases → Draft a new release
2. Choose tag: `v1.0.0`
3. Title: `Frontend UI v1.0.0`
4. Description:
```markdown
## 🎉 GPT Storyworld Frontend v1.0.0

First release of the interactive React frontend for GPT Storyworld!

### ✨ Features
- 🎛️ Visual parameter configuration
- 🔑 Secure API key management
- 📝 Custom prompt additions
- 👁️ System prompt preview
- 💾 Automatic JSON export
- 📱 Responsive design

### 📦 Installation
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

### 📚 Documentation
- [README.md](frontend/README.md)
- [Integration Guide](frontend/INTEGRATION.md)
- [Deployment Guide](frontend/DEPLOYMENT.md)
```

5. Attach `gpt-storyworld-frontend.tar.gz` as binary

## Enable GitHub Pages (Optional)

Host the demo:

```bash
# Build the app
cd frontend
npm run build

# The dist/ folder contains static files
# Push to gh-pages branch:
git checkout -b gh-pages
cp -r dist/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

Then in repo settings:
- Settings → Pages
- Source: `gh-pages` branch
- Your site will be at: `https://patrickdugan.github.io/GPTStoryworld/`

## Promotion Ideas

### Twitter/X Post
```
🎮 Just released GPT Storyworld Frontend v1.0!

Generate Sweepweave-compatible interactive narratives with a beautiful React UI

✨ Visual config, GPT-4 integration, JSON export
🔗 github.com/patrickdugan/GPTStoryworld

#AI #GameDev #OpenAI #React
```

### Reddit Post (r/gamedev, r/programming)
```
[Project] GPT Storyworld - React UI for AI-powered narrative generation

Built a frontend for my GPT-based storyworld generator. It lets you 
configure parameters visually and generates structured JSON encounters 
for interactive fiction/games.

Tech: React, Vite, OpenAI API
Repo: [link]
Demo: [link]

Feedback welcome!
```

## Next Steps

- [ ] Push to GitHub
- [ ] Create release
- [ ] Update main README
- [ ] Add repository topics
- [ ] Consider GitHub Pages for demo
- [ ] Share on social media
- [ ] Submit to awesome-gpt lists

---

Happy shipping! 🚀
