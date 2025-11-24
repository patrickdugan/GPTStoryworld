# GPT Storyworld Frontend

A sleek, modern frontend interface for generating **Sweepweave-compatible interactive storyworlds** using the GPT API.

![GPT Storyworld](https://img.shields.io/badge/GPT-Storyworld-blueviolet)
![React](https://img.shields.io/badge/React-18.2-blue)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF)

## ✨ Features

- **Interactive Configuration**: Adjust storyworld parameters with intuitive sliders
  - Number of characters (1-10)
  - Thematic elements (1-5)
  - Tracked variables (3-20)
  - Encounter length (200-1500 words)

- **Custom Instructions**: Add your own system prompt additions for fine-tuned generation

- **API Key Management**: Secure local storage of OpenAI API credentials with a clean config modal

- **System Prompt Preview**: View the exact prompt that will be sent to GPT before generating

- **Direct GPT Integration**: Makes real-time calls to OpenAI's API (supports GPT-4)

- **JSON Export**: Automatically downloads generated storyworlds as JSON files

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/patrickdugan/GPTStoryworld.git
cd GPTStoryworld

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will open at `http://localhost:3000`

### Building for Production

```bash
npm run build
npm run preview
```

## 🎮 Usage

1. **Configure API Key**: Click the gear icon ⚙️ in the top-right and enter your OpenAI API key

2. **Adjust Parameters**: Use the sliders to set:
   - How many characters your storyworld should have
   - Number of central themes
   - Tracked state variables
   - Target word count per encounter

3. **Add Custom Instructions** (Optional): Enter additional prompt text to guide the generation

4. **Preview Prompt**: Click "Preview Prompt" to see the exact system prompt

5. **Generate**: Hit "Generate Storyworld" and your JSON file will download automatically

## 🏗️ Architecture

```
src/
├── App.jsx           # Main React component with state management
├── App.css           # Styled gradient UI with glassmorphism effects
├── main.jsx          # React entry point
└── index.css         # Global CSS reset

Key Features:
- Direct OpenAI API integration (no backend required)
- Local storage for API key persistence
- Responsive design (mobile-friendly)
- Modal-based configuration UI
```

## 🎨 System Prompt Structure

The generator creates a comprehensive system prompt that includes:

```json
{
  "encounter": "Generated narrative text",
  "choices": ["choice1", "choice2", "choice3"],
  "variables_affected": {"reputation": +5, "gold": -20},
  "metadata": {
    "characters_present": ["Alice", "Bob"],
    "themes_emphasized": ["betrayal", "redemption"],
    "narrative_weight": 8
  }
}
```

## 🔒 Security

- API keys are stored in `localStorage` only
- Keys are never sent anywhere except directly to OpenAI
- No backend server = no key exposure risk
- Uses HTTPS for all API calls

## 🛠️ Tech Stack

- **React 18.2**: Component-based UI
- **Vite 5**: Lightning-fast dev server and bundling
- **Lucide React**: Beautiful, consistent icons
- **OpenAI API**: GPT-4 powered generation

## 📝 Customization

### Modify Slider Ranges

Edit the `min`, `max`, and `step` attributes in `App.jsx`:

```jsx
<input
  type="range"
  min="1"
  max="10"
  value={config.numCharacters}
  onChange={(e) => handleSliderChange('numCharacters', e.target.value)}
/>
```

### Change Color Scheme

Update the gradient in `App.css`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adjust GPT Model

Modify the API call in `App.jsx`:

```jsx
body: JSON.stringify({
  model: 'gpt-4-turbo-preview', // or 'gpt-3.5-turbo'
  messages: [...],
  temperature: 0.8,
  max_tokens: config.encounterLength * 2
})
```

## 🤝 Integration with Original Repo

This frontend is designed to complement the [original GPT Storyworld CLI tool](https://github.com/patrickdugan/GPTStoryworld). You can:

1. Use the frontend to generate initial encounters
2. Feed the JSON output into the CLI for iterative expansion
3. Track metadata balance via `meta.json` as described in the original repo

## 📄 License

MIT - feel free to fork, modify, and use commercially!

## 🐛 Issues & Contributions

Found a bug or have a feature request? Open an issue on GitHub!

PRs welcome - let's make storyworld generation even better.

---

**Built with ❤️ for narrative AI researchers and game designers**

Connect: [@patrickdugan](https://github.com/patrickdugan)
