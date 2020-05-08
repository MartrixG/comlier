class element(object):
    def __init__(self, name):
        if name[0] == '/':
            self.name = name[1:]
            self.type = "VN"
        else:
            self.name = name
            if self.name == '#':
                self.type = 'epsilon'
            else:
                self.type = 'VT'

    def __str__(self):
        return self.name + '_' + self.type.lower()

    def __repr__(self):
        return self.name + '_' + self.type.lower()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.name + " " + self.type)

    def __lt__(self, other):
        if self.type != other.type:
            return self.type == 'VT'
        return self.name.lower() < other.name.lower()