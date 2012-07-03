
import os
import pickle

class serializlist:

    def __init__(self, filename):
        self.filename = filename
        self.container = list();
        self.fetch()

    def __del__(self):
        self.update()

    def __contains__(self, value):
        return value in self.container
    
    def append(self, value):
        self.container.append(value)
    
    def fetch(self):

        if os.path.exists(self.filename) :
            with open(self.filename, 'r') as f:
                data = pickle.Unpickler(f)
                self.container = data.load();

        else:
            open(self.filename, 'w').close()

    def update(self):

        with open(self.filename, 'w+') as f:
            data = pickle.Pickler(f)
            data.dump(self.container)
