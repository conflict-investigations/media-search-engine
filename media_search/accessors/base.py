import json
import os

class DataSource():
    def __init__(self, datapath=None):
        # To be used later for determining storage locations
        if not datapath:
            datapath = os.getcwd()
        self.datapath = datapath
        self.filename = 'base.json'

    def load_data(self):
        with open(os.path.join(self.datapath, self.filename), 'r') as f:
            data = json.load(f)
        return data

    def dump_data(self, data):
        with open(os.path.join(self.datapath, self.filename), 'w') as f:
            json.dump(data, f)

    def get_data(download=True):
        raise NotImplementedError

    def print_data(download=True):
        raise NotImplementedError
