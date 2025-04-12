class Environment:
    def __init__(self, enclosing=None):
        self.variables = {}
        self.enclosing = enclosing  # Optional parent environment (for local scopes)

    def define(self, name, value):
        self.variables[name] = value

    def assign(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise NameError(f"Undefined variable '{name}'")

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.enclosing:
            return self.enclosing.get(name)
        else:
            raise NameError(f"Undefined variable '{name}'")

    def __contains__(self, name):
        return name in self.variables or (self.enclosing and name in self.enclosing)

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, value):
        self.assign(name, value)
