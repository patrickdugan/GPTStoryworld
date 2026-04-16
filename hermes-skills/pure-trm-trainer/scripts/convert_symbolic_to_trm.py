import json
from pathlib import Path

def convert_symbolic_traces(runs_root, out_file):
    runs_root = Path(runs_root)
    converted = []
    
    for episode_file in runs_root.glob("*/episode.jsonl"):
        with open(episode_file, 'r', encoding='utf-8') as f:
            for line in f:
                row = json.loads(line)
                if "visible_state" in row and "route" in row and "action" in row:
                    # visible_state -> user prompt
                    # route -> assistant routing decision
                    # action -> actual symbolic behavior
                    
                    system_prompt = "You are a TRM Controller. Emit compact JSON routing and action decisions."
                    user_content = row["visible_state"]
                    
                    route_data = row["route"]
                    assistant_payload = {
                        "route": route_data.get("route", "UNKNOWN"),
                        "rationale": route_data.get("rationale", ""),
                        "action": row["action"],
                        "agent": row.get("agent", "unknown")
                    }
                    
                    converted.append({
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content},
                            {"role": "assistant", "content": json.dumps(assistant_payload)}
                        ],
                        "meta": {
                            "source_run": episode_file.parent.name,
                            "step": row.get("step", 0)
                        }
                    })
    
    out_path = Path(out_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        for item in converted:
            f.write(json.dumps(item) + '\n')
            
    return len(converted)

if __name__ == "__main__":
    count = convert_symbolic_traces("verifiers_envs/storyworld-symbolic-env/runs", "hermes-skills/pure-trm-trainer/runs/symbolic_controller_v1/train.jsonl")
    print(f"Converted {count} symbolic trace steps.")
