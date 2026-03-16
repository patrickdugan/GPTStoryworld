#!/usr/bin/env python3
import json
import sys
import os

# Add missing fields to storyworld
def add_missing_fields(filename):
    try:
        text = open(filename, 'r').read()
        world = json.loads(text)
        
        # Add required fields
        world['css_theme'] = 'classic'
        world['debug_mode'] = False
        world['display_mode'] = 'desktop'
        world['authored_properties'] = []

        # Convert chars to characters format if needed
        if 'chars' in world:
            world['characters'] = world['chars']
            del world['chars']

        # Add minimum authored properties structure
        for char in world.get('characters', []):
            world['authored_properties'].append({
                "id": f"Embodiment_Virtuality_{char['id']}" ,
                "default_value": 0,
                "depth": 0,
                "affected_characters": [char['id']]
            })
    
        # Write back
        with open(filename, 'w') as f:
            json.dump(world, f, indent=2)
            
        print(f"Added missing fields to {filename}")
        return world
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_validation_fields.py <storyworld_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    success = add_missing_fields(filename, verbose=True)
    sys.exit(0 if success else 1)
