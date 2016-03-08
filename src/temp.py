import pickle

import layout

def doTempStuff():
    
    dumpPickledProj("sf2.caravan-game")

def dumpPickledProj(fn):
    
    proj = layout.Project("Shining Force 2")
    
    f = file(fn, "wb")
    pickle.dump(proj, f, -1)
    f.close()