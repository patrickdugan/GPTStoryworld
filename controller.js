import fs from 'fs/promises';
import { buildNextPrompt } from './promptGenerator.js';
import { config } from 'dotenv';
import OpenAI from 'openai';
import { exec } from 'child_process';

config();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const ENCOUNTERS_PATH = './raw_storyworld.json';

async function generateEncounter(prompt) {
  const completion = await openai.chat.completions.create({
    model: "gpt-4",
    temperature: 0.7,
    messages: [
      { role: "system", content: "You are an expert Sweepweave encounter generator." },
      { role: "user", content: prompt }
    ]
  });

  const responseText = completion.choices[0].message.content;
  try {
    const jsonStart = responseText.indexOf('{') !== -1 ? responseText.indexOf('{') : responseText.indexOf('[');
    return JSON.parse(responseText.slice(jsonStart).trim());
  } catch (err) {
    console.error("❌ Failed to parse GPT output:", err.message);
    console.log(responseText);
    return null;
  }
}

async function run() {
  const prompt = await buildNextPrompt();
  const newEncounter = await generateEncounter(prompt);
  if (!newEncounter) return;

  const raw = await fs.readFile(ENCOUNTERS_PATH, 'utf8');
  const story = JSON.parse(raw);
  story.encounters.push(newEncounter);
  await fs.writeFile(ENCOUNTERS_PATH, JSON.stringify(story, null, 2));
  console.log("✅ Encounter added to raw_storyworld.json");

  exec('node meta-calc.js', (err, stdout, stderr) => {
    if (err) console.error(stderr);
    else console.log(stdout);
  });
}

run();
