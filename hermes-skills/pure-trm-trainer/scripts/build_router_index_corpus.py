import json
import argparse
from pathlib import Path

def generate_index_lookup_dataset(corpus_path, output_path):
    """
    Converts a storyworld corpus (encounters, lore, characters) into 
    TRM-router training examples for Index Lookup.
    """
    examples = []
    
    # Load corpus (assuming JSONL for now based on conveyor exports)
    with open(corpus_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            
            # Scenario: Character needs specific lore or encounter data
            # TRM Goal: Map this need to a tool call
            
            # Example 1: Encounter Lookup
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY the tool call needed to fetch relevant context."},
                    {"role": "user", "content": f"The player is at node '{data.get('parent_node', 'root')}' and chose '{data.get('last_action', 'explore')}'. Prepare the next encounter."},
                    {"role": "assistant", "content": f'{{ "tool": "get_encounter_card", "args": {{ "id": "{data.get("id", "unknown")}" }} }}'}
                ]
            })
            
            # Example 2: Lore Retrieval
            if "tags" in data:
                for tag in data["tags"]:
                    examples.append({
                        "messages": [
                            {"role": "system", "content": "You are a TRM Index Router. Map keywords to lore namespaces."},
                            {"role": "user", "content": f"Query: What are the historical precedents for {tag} in this world?"},
                            {"role": "assistant", "content": f'{{ "tool": "query_lore_index", "args": {{ "namespace": "history", "query": "{tag}" }} }}'}
                        ]
                    })

    with open(output_path, 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex) + '\n')
    
    print(f"Generated {len(examples)} TRM index-router examples -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_index_lookup_dataset(args.corpus, args.output)
