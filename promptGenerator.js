import fs from 'fs/promises';
import meta from './meta.json' assert { type: 'json' };

const THEMES = [
  "deception vs. mercy",
  "hierarchy vs. equality",
  "sacrifice vs. consent",
  "bias in training data",
  "moral agency in war",
  "legitimacy vs. power",
  "transparency vs. stability"
];

function pickRandomTheme(themes) {
  return themes[Math.floor(Math.random() * themes.length)];
}

async function readIdeaFactory() {
  try {
    const tropes = await fs.readFile('./tropes/spool_design.md', 'utf-8');
    const math = await fs.readFile('./tropes/math_patterns.md', 'utf-8');
    const history = await fs.readFile('./tropes/myth_history.md', 'utf-8');
    return [tropes, math, history].join('\n\n').trim();
  } catch {
    return '';
  }
}

export async function buildNextPrompt() {
  const { average_effects_per_reaction, dominant_properties, effect_types } = meta;

  const focusProperty = dominant_properties.find(
    prop => !Object.keys(effect_types).some(type => type.includes(prop))
  ) || "EmpathyBuffer";

  const theme = pickRandomTheme(THEMES);

  const ideaFactory = await readIdeaFactory();

  const prompt = `
Generate a Sweepweave 1.9 JSON-format encounter in an interactive storyworld.

- Themes: ${THEMES.join(", ")}
- Focus: Add moral depth and effects on "${focusProperty}"
- Structure: 2+ options, each with 1+ reactions, each with effects
- Style: Characters should be thoughtful and distinct
 - Diversity notes: ${ideaFactory}

Respond with valid Sweepweave 1.9 JSON only.
`;

  await fs.writeFile('./last_prompt.txt', prompt.trim());
  return prompt.trim();
}
