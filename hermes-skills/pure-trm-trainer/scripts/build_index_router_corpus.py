import json
import random
from pathlib import Path

def generate_synthetic_router_data(storyworld_path: str, output_path: str):
    with open(storyworld_path, 'r') as f:
        world = json.load(f)
    
    pages = world.get("pages", {})
    characters = world.get("characters", [])
    namespaces = ["constitutions", "history", "geography", "mechanics"]
    
    dataset = []
    
    # Generate Encounter Lookups
    for page_id in list(pages.keys())[:50]:
        query = f"I need the details for the encounter at {page_id}."
        target = {"tool": "get_encounter_card", "args": {"encounter_id": page_id}}
        dataset.append({"prompt": query, "completion": json.dumps(target)})
    
    # Generate Lore Queries
    for char in characters:
        name = char.get("name", "the character")
        query = f"Tell me about {name}'s background and motivations."
        target = {"tool": "query_lore_index", "args": {"namespace": "characters", "query": name}}
        dataset.append({"prompt": query, "completion": json.dumps(target)})
        
    # Generate System Queries
    for ns in namespaces:
        query = f"What are the {ns} rules for this world?"
        target = {"tool": "query_lore_index", "args": {"namespace": ns, "query": "general"}}
        dataset.append({"prompt": query, "completion": json.dumps(target)})

    with open(output_path, 'w') as f:
        for entry in dataset:
            # Format for Qwen-Chat / Hermes-style messages
            msg = {
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Map queries to fetch actions."},
                    {"role": "user", "content": entry["prompt"]},
                    {"role": "assistant", "content": entry["completion"]}
                ]
            }
            f.write(json.dumps(msg) + "\n")
    print(f"Generated {len(dataset)} examples at {output_path}")

if __name__ == "__main__":
    # Example usage targeting the Ashen Aegis world
    generate_synthetic_router_data(
        "storyworlds/charter_of_ashen_aegis.json", 
        "hermes-skills/pure-trm-trainer/runs/index_router_v1.jsonl"
    )
