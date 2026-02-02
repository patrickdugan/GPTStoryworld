
import json, sys
world=json.load(open(sys.argv[1]))
pid,opt=sys.argv[2],sys.argv[3]
for e in world["encounters"]:
    if e["id"]==pid:
        for o in e["options"]:
            if o["id"]==opt: o["secret"]=True
json.dump(world,open(sys.argv[1],"w"),indent=2)
