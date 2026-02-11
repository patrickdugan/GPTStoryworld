#!/bin/bash

echo "🎮 GPT Storyworld Frontend Setup"
echo "================================"
echo ""

# Check if node is installed
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Get your OpenAI API key from https://platform.openai.com/api-keys"
    echo "   2. Run: npm run dev"
    echo "   3. Click the ⚙️ gear icon to add your API key"
    echo "   4. Start generating storyworlds!"
    echo ""
    echo "📚 Documentation:"
    echo "   - README.md for usage guide"
    echo "   - INTEGRATION.md for CLI integration"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
