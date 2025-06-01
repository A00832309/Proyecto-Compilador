class Mmemoria:
    def __init__(self):
        self.ranges = {
            'global': {'int': 1000, 'float': 2000, 'bool': 3000},
            'local': {'int': 4000, 'float': 5000, 'bool': 6000},
            'constant': {'int': 7000, 'float': 8000, 'bool': 9000},
            'temp': {'int': 10000, 'float': 11000, 'bool': 12000}
        }
        self.memory = {
            'global': {'int': {}, 'float': {}, 'bool': {}},
            'local': {'int': {}, 'float': {}, 'bool': {}},
            'constant': {'int': {}, 'float': {}, 'bool': {}},
            'temp': {'int': {}, 'float': {}, 'bool': {}}
        }

    def get_address(self, scope, var_name, var_type):
        if var_name in self.memory[scope][var_type]:
            return self.memory[scope][var_type][var_name]

        addr = self.ranges[scope][var_type]
        self.memory[scope][var_type][var_name] = addr
        self.ranges[scope][var_type] += 1
        return addr

    def get_constant_address(self, value, var_type):
        if value in self.memory['constant'][var_type]:
            return self.memory['constant'][var_type][value]

        addr = self.ranges['constant'][var_type]
        self.memory['constant'][var_type][value] = addr
        self.ranges['constant'][var_type] += 1
        return addr

    def get_temp_address(self, var_type):
        addr = self.ranges['temp'][var_type]
        self.ranges['temp'][var_type] += 1
        return addr
