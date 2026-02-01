
import json, sys
from collections import OrderedDict
def load(p): return json.load(open(p,"r",encoding="utf-8"))
def save(p,d): json.dump(d,open(p,"w",encoding="utf-8"),indent=2)
if len(sys.argv)!=4: sys.exit(1)
world=load(sys.argv[1])
enc=OrderedDict({"id":sys.argv[2],"title":sys.argv[3],"text":"","options":[],"connected_spools":[]})
world["encounters"].append(enc); save(sys.argv[1],world)
