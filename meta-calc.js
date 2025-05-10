import fs from 'fs/promises';

const INPUT_PATH = './raw_storyworld.json';
const OUTPUT_PATH = './meta.json';

const calcMeta = async () => {
  const raw = await fs.readFile(INPUT_PATH, 'utf8');
  const data = JSON.parse(raw);
  const encounters = data.encounters || [];
  const numEncounters = encounters.length;
  const characters = data.storyworld_model.characters || [];
  const dominantProps = data.storyworld_model.dominant_properties || [];

  let totalOptions = 0, totalReactions = 0, totalEffects = 0, encountersWith2OptsAndReacts = 0;
  const effectTypes = {};

  for (const enc of encounters) {
    const opts = enc.options || [];
    totalOptions += opts.length;
    let validOpts = 0;

    for (const opt of opts) {
      const reacts = opt.reactions || [];
      totalReactions += reacts.length;
      if (reacts.length >= 1) validOpts++;
      for (const r of reacts) {
        const effects = r.after_effects || [];
        totalEffects += effects.length;
        for (const eff of effects) {
          const type = eff.effect_type || 'unknown';
          effectTypes[type] = (effectTypes[type] || 0) + 1;
        }
      }
    }
    if (opts.length >= 2 && validOpts >= 2) encountersWith2OptsAndReacts++;
  }

  const meta = {
    total_encounters: numEncounters,
    total_characters: characters.length,
    dominant_properties: dominantProps,
    total_options: totalOptions,
    total_reactions: totalReactions,
    total_effects: totalEffects,
    effect_types: effectTypes,
    encounters_with_2_opts_and_reacts: encountersWith2OptsAndReacts,
    percent_with_2_opts_2_reacts: numEncounters ? +(100 * encountersWith2OptsAndReacts / numEncounters).toFixed(2) : 0,
    average_options_per_encounter: numEncounters ? +(totalOptions / numEncounters).toFixed(2) : 0,
    average_reactions_per_option: totalOptions ? +(totalReactions / totalOptions).toFixed(2) : 0,
    average_effects_per_reaction: totalReactions ? +(totalEffects / totalReactions).toFixed(2) : 0
  };

  await fs.writeFile(OUTPUT_PATH, JSON.stringify(meta, null, 2));
  console.log(`✅ Meta written to ${OUTPUT_PATH}`);
};

calcMeta().catch(err => console.error('❌ Failed:', err));
