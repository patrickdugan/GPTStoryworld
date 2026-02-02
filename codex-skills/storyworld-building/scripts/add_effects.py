
import json, sys
world=json.load(open(sys.argv[1]))
pid,opt,i=sys.argv[2],sys.argv[3],int(sys.argv[4])
for e in world["encounters"]:
    if e["id"]==pid:
        for o in e["options"]:
            if o["id"]==opt:
                o["reactions"][i].setdefault("after_effects",[]).append(
                  {"Set":{"property":"","to":{"Operator":"Add","value":0.0}}})
json.dump(world,open(sys.argv[1],"w"),indent=2)
