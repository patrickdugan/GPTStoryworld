#!/usr/bin/env python3
"""Fix visibility - make all options always visible."""

import json
from pathlib import Path

WORLD_PATH = Path('/mnt/c/projects/GPTStoryworld/storyworlds/factory_runs/the_diamond_job/polished_world.json')

with open(WORLD_PATH) as f:
    world = json.load(f)

for enc in world['encounters']:
    if not enc['id'].startswith('page_end_'):
        for opt in enc.get('options', []):
            opt['visibility_script'] = True
            opt['performability_script'] = True

with open(WORLD_PATH, 'w') as f:
    json.dump(world, f, indent=2)

print("Fixed visibility for all options")

# Verify
with open(WORLD_PATH) as f:
    w = json.load(f)

enc = w['encounters'][0]
print(f"\nFirst encounter: {enc['id']}")
print(f"Options: {len(enc['options'])}")
for i, opt in enumerate(enc['options']):
    print(f"  Option {i}: visibility = {opt.get('visibility_script')}")