
import json 
class managerjson:
    def __init__(self, filerute):
        self.filerute = filerute
        self.data = self._load_config()

    def _load_config(self):
        with open(self.filerute) as config_file:
            return json.load(config_file)

    def _save_config(self):
        with open(self.filerute, 'w') as config_file:
            json.dump(self.data, config_file, indent=4)

    def update(self, rute, value):
        if self.get(rute) is not None:
            arrayrute = rute.split("/")
            data = self.data
            for r in arrayrute[:-1]:
                data = data[r]
            data[arrayrute[-1]] = value
            self._save_config()
            return(self.get(rute))
        else:
            return None

    def get(self, rute):
        data = self.data
        for r in rute.split("/"):
            if r not in data:
                return None
            data = data[r]
        return data

    def set(self, route, value):
        arrayrute = route.split("/")
        data = self.data
        for r in arrayrute[:-1]:
            if r not in data:
                data[r] = {}
            data = data[r]
        data[arrayrute[-1]] = value
        self._save_config()
        if self.get(route) is not None:
            return True
        else: return False

    def delete(self, route):
        arrayrute = route.split("/")
        data = self.data
        for r in arrayrute[:-1]:
            if r not in data:
                return
            data = data[r]

        if arrayrute[-1] in data:
            del data[arrayrute[-1]]
        self._save_config()
        if self.get(route) is None:
            return True
        else: return False

#m=managerconfig('static/config/config.json')
