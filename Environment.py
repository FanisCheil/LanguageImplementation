class Environment:
    def __init__(self, enclosing=None):
        self.variables = {}  # Dictionary to store variables in the current scope
        self.enclosing = enclosing  # Parent environment (used for nested scopes or closures)

    def define(self, name, value):
        self.variables[name] = value  # Always defines a new variable in the current local scope

    def assign(self, name, value):
        if name in self.variables:
            self.variables[name] = value  # If variable exists in current scope, update it
        elif self.enclosing and name in self.enclosing:
            self.enclosing.assign(name, value)  # Otherwise, delegate assignment to parent scope
        else:
            raise NameError(f"Undefined variable '{name}'")  # Variable not declared anywhere

    def get(self, name):
        if name in self.variables:
            return self.variables[name]  # Return variable from current scope
        elif self.enclosing:
            return self.enclosing.get(name)  # Look for variable in parent environment
        else:
            raise NameError(f"Undefined variable '{name}'")  # Variable not found

    def __contains__(self, name):
        return name in self.variables or (self.enclosing and name in self.enclosing)
        # Check whether variable exists in current or any enclosing scope

    def __getitem__(self, name):
        return self.get(name)  # Allows environment[name] to access variables like a dictionary

    def __setitem__(self, name, value):
        self.assign(name, value)  # Allows environment[name] = value syntax for assignment
