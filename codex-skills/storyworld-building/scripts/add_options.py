
import json, sys
world=json.load(open(sys.argv[1]))
pid=sys.argv[2]
for e in world["encounters"]:
    if e["id"]==pid:
        for l in sys.argv[3:]:
            e["options"].append({"id":f"opt_{len(e['options'])+1}","text":l,"reactions":[]})
json.dump(world,open(sys.argv[1],"w"),indent=2)
