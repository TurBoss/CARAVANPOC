import pickle

def init(filename):
    
    try:
        f = file(filename, "rb")
        cfg = pickle.load(f)
        f.close()
    
    except IOError, e:
        cfg = CaravanSettings(filename)
        cfg.save()
    
    return cfg
    
class CaravanSettings(object):
    
    def __init__(self, filename):
        
        self.filename = filename
        
        self.options = {}
        self.platforms = {}
        self.games = {}
        
        self.history = {}
        
        self.history["ROMs"] = []
        
    def save(self):
        
        f = file(self.filename, "wb")
        pickle.dump(self, f, -1)
        f.close()
        