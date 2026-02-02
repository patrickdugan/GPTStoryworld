
# Sweepweave Validator + Normalizer
# Usage:
#   python sweepweave_validator.py validate file.json
#   python sweepweave_validator.py normalize in.json out.json [ref.json]

import json, sys, time, uuid
from collections import OrderedDict

def now_ts():
    return float(time.time())

def validate_storyworld(path: str):
    import os
    errors = []
    if not os.path.exists(path):
        return [f"File not found: {path}"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"JSON parse error: {e}"]
    required_top = ["IFID","about_text","css_theme","debug_mode","display_mode","creation_time","modified_time","characters","authored_properties","spools","encounters"]
    for k in required_top:
        if k not in data:
            errors.append(f"{k}: missing")
    return errors

def normalize_storyworld(input_path: str, output_path: str, reference_path: str):
    with open(reference_path,"r",encoding="utf-8") as f:
        ref = json.load(f, object_pairs_hook=OrderedDict)
    with open(input_path,"r",encoding="utf-8") as f:
        test = json.load(f, object_pairs_hook=OrderedDict)

    normalized = OrderedDict()
    for key in ref.keys():
        normalized[key] = test.get(key, ref[key])

    # Preserve authored spools & encounters verbatim after key-order merge
    # (prevents wiping nested fields like connected_spools by ref defaults)
    if "spools" in test:
        normalized["spools"] = test["spools"]
    if "encounters" in test:
        normalized["encounters"] = test["encounters"]

    import uuid, time
    if not isinstance(normalized.get("IFID",""), str) or len(normalized["IFID"]) < 10:
        normalized["IFID"] = str(uuid.uuid4())

    for k in ["creation_time", "modified_time"]:
        if k in normalized:
            normalized[k] = float(normalized[k])

    with open(output_path,"w",encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)

    return output_path

if __name__=="__main__":
    if len(sys.argv)<3:
        print("Usage: python sweepweave_validator.py (validate|normalize) file.json [out.json ref.json]")
        sys.exit(1)
    mode=sys.argv[1]
    if mode=="validate":
        errs=validate_storyworld(sys.argv[2])
        if errs:
            print("Invalid:",errs); sys.exit(2)
        print("VALID ✅")
    elif mode=="normalize":
        out=sys.argv[3] if len(sys.argv)>3 else "normalized.json"
        ref=sys.argv[4] if len(sys.argv)>4 else "dogs_in_a_barrel_secret_endings_spools.json"
        path=normalize_storyworld(sys.argv[2],out,ref)
        print("Normalized written to",path)
