from abc import ABC, abstractmethod 
from Token import Token, TokenType
from typing import List
from Environment import Environment



#Parent class for all expression types
class Expression(ABC):
    @abstractmethod #This forces all subclasses to implement the evaluate() function
    def evaluate(self, env, verbose=True): #Method which evaluates the expression
        pass

# Handles binary operations like 5 + 3, true and false, etc.
class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
        self.left = left  # The left operand (another expression)
        self.operator = operator  # The operator token (e.g., +, -, *, /, or, and, etc.)
        self.right = right  # The right operand (another expression)

    def evaluate(self, env, verbose=True):
        # Recursively evaluate the left and right sides of the expression
        left_value = self.left.evaluate(env, verbose)
        right_value = self.right.evaluate(env, verbose)

        # Debug print to show what's being evaluated
        if verbose:
            print(f"Evaluating: {left_value} {self.operator.lexeme} {right_value}")

        # Boolean logic: both operands must be booleans for 'and' / 'or'
        if self.operator.type == TokenType.AND:
            if isinstance(left_value, bool) and isinstance(right_value, bool):
                return left_value and right_value
            raise TypeError(f"Cannot use 'and' between {type(left_value).__name__} and {type(right_value).__name__}.")
        elif self.operator.type == TokenType.OR:
            if isinstance(left_value, bool) and isinstance(right_value, bool):
                return left_value or right_value
            raise TypeError(f"Cannot use 'or' between {type(left_value).__name__} and {type(right_value).__name__}.")

        # Equality checks (== and !=) work on any types
        if self.operator.type == TokenType.EQUAL_EQUAL:
            return left_value == right_value  # e.g. 5 == 5, "hi" == "hi"
        elif self.operator.type == TokenType.BANG_EQUAL:
            return left_value != right_value  # e.g. 5 != 10, true != false

        # Comparison operators (<, <=, >, >=) — only valid for numbers
        elif self.operator.type in (TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                if self.operator.type == TokenType.LESS:
                    return left_value < right_value
                elif self.operator.type == TokenType.LESS_EQUAL:
                    return left_value <= right_value
                elif self.operator.type == TokenType.GREATER:
                    return left_value > right_value
                elif self.operator.type == TokenType.GREATER_EQUAL:
                    return left_value >= right_value
            raise TypeError(f"Cannot compare '{type(left_value).__name__}' with '{type(right_value).__name__}'.")

        # Addition operator (+) can support numbers, strings, or lists
        if self.operator.type == TokenType.PLUS:
            # String concatenation
            if isinstance(left_value, str) and isinstance(right_value, str):
                return left_value + right_value  # "hello" + "world" => "helloworld"
            # Numeric addition
            elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value + right_value  # 5 + 3 => 8
            # List concatenation
            elif isinstance(left_value, list) and isinstance(right_value, list):
                return left_value + right_value  # [1,2] + [3,4] => [1,2,3,4]
            # Invalid types for +
            else:
                raise TypeError(f"Cannot use '+' between {type(left_value).__name__} and {type(right_value).__name__}.")

        # For -, *, /, %, **, both operands must be numbers
        if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
            raise TypeError(f"Invalid operation: Cannot use '{self.operator.lexeme}' between {type(left_value).__name__} and {type(right_value).__name__}.")

        # Subtraction
        if self.operator.type == TokenType.MINUS:
            return left_value - right_value
        # Multiplication
        elif self.operator.type == TokenType.TIMES:
            return left_value * right_value
        # Division (check for division by zero)
        elif self.operator.type == TokenType.DIV:
            if right_value == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left_value / right_value
        # Modulo
        elif self.operator.type == TokenType.MOD:
            return left_value % right_value
        # Exponentiation with overflow protection
        elif self.operator.type == TokenType.EXP:
            if abs(left_value) > 999 or abs(right_value) > 999:
                raise OverflowError("Number too large to compute.")
            return left_value ** right_value

        # Fallback for unrecognized operators
        else:
            raise ValueError(f"Unsupported operator: {self.operator.lexeme}")

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.left} {self.right})"


class Unary(Expression):
    def __init__(self, operator: Token, operand: Expression) -> None:
        self.operator = operator
        self.operand = operand

    def evaluate(self, env, verbose=True):
        operand_value = self.operand.evaluate(env, verbose) # recursively evaluate the operand before applying the unary operation

        #Boolean negation like !true -> false
        if self.operator.type == TokenType.BANG:
            if isinstance(operand_value, bool): #ensure only booleans are negated
                return not operand_value
            raise TypeError(f"Cannot apply '!' to {type(operand_value).__name__}.")

        if not isinstance(operand_value, (int, float)):
            raise TypeError(f"Invalid unary operation: Cannot apply '{self.operator.lexeme}' to {type(operand_value).__name__}.")
        
        #Negation
        if self.operator.type == TokenType.MINUS:
            return -operand_value
            # -(3+2) -> 5
          
        return operand_value  

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.operand})"

class Literal(Expression):

    #Store consatnt values
    def __init__(self, value: object) -> None:
        self.value = value
    
    #Return the stored value and ensure it is a valid type
    def evaluate(self, env, verbose=True):
        if isinstance(self.value, (int, float, str, bool)):
            return self.value
        raise TypeError(f"Invalid literal: Expected number, string, or boolean but got {type(self.value).__name__}.")

    def __str__(self) -> str:
        return f"{self.value}"

class Grouping(Expression):

    #Store an inner expression like (5 +3) * 2
    def __init__(self, expression: Expression) -> None:
        self.expression = expression
    
    #Evaluate the inner expression
    def evaluate(self, env, verbose=True):
        return self.expression.evaluate(env, verbose)

    def __str__(self) -> str:
        return f"(group {self.expression})"

# Handles variable references like `x`
class Variable(Expression):
    def __init__(self, name: Token):
        self.name = name  # Store the variable name token

    def evaluate(self, env, verbose=True):
        # Look up the value of the variable in the current environment
        return env.get(self.name.lexeme)
    
    def __str__(self) -> str:
        return f"{self.name.lexeme}"

# Handles variable assignments like `x = 5`
class Assignment(Expression):
    def __init__(self, name: Token, value_expr: Expression):
        self.name = name  # The variable name
        self.value_expr = value_expr  # The expression whose result will be assigned

    def evaluate(self, env, verbose=True):
        # Evaluate the right-hand side of the assignment
        value = self.value_expr.evaluate(env, verbose)

        if self.name.lexeme in env:
            env.assign(self.name.lexeme, value)  # If the variable exists, update it
        else:
            env.define(self.name.lexeme, value)  # Otherwise, create it in the current scope
        return value
    
    def __str__(self) -> str:
        return f"(assign {self.name.lexeme} = {self.value_expr})"

# Handles print statements like `print x`
class Print(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions  # List of expressions to print

    def evaluate(self, env, verbose=True):
        result = ""
        for expr in self.expressions:
            value = expr.evaluate(env, verbose)  # Evaluate each expression
            result += str(value)  # Convert each to string and concatenate
        print(result)  # Print the final output
        return None  # Print does not return a value

# Handles input from the user using ask "Prompt"
class Ask(Expression):
    def __init__(self, prompt_expr: Expression):
        self.prompt_expr = prompt_expr  # The expression to display as a prompt

    def evaluate(self, env, verbose=True):
        prompt = self.prompt_expr.evaluate(env, verbose)  # Evaluate prompt expression
        if not isinstance(prompt, str):
            raise TypeError("ask expects a string prompt")
        return input(prompt).strip()  # Prompt the user and return stripped input

    def __str__(self) -> str:
        return f"(ask {self.prompt_expr})"



# Handles if/elsif/else control flow logic
class IfChain(Expression):
    def __init__(self, conditions: list, else_branch: list = None):
        self.conditions = conditions  # List of (condition, block) tuples: supports if + multiple elsif branches
        self.else_branch = else_branch  # Optional else block (list of statements)

    def evaluate(self, env, verbose=True):
        # Loop over each (condition, block) pair in the if-elsif chain
        for idx, (condition, block) in enumerate(self.conditions):
            result = condition.evaluate(env, verbose)  # Evaluate the condition expression

            if not isinstance(result, bool):  # Ensure the condition is boolean
                raise TypeError("Condition must evaluate to boolean.")

            if result:  # If condition is true, execute its block
                local_env = Environment(env)  # New local scope for this branch
                last_value = None
                for stmt in block:
                    last_value = stmt.evaluate(local_env, verbose)  # Evaluate each statement in the block
                return last_value  # Return result of the last statement in the block

        # If none of the if/elsif conditions matched, check for optional else
        if self.else_branch:
            if verbose:
                print("[DEBUG] No condition matched. Executing else branch.")
            local_env = Environment(env)  # New local scope for the else block
            last_value = None
            for stmt in self.else_branch:
                last_value = stmt.evaluate(local_env, verbose)
            return last_value  # Return result of last statement in else block

        return None  # If no condition matches and no else block, return nothing

    def __str__(self):
        # String representation of the full if-elsif-else structure
        s = ""
        for i, (cond, block) in enumerate(self.conditions):
            if i == 0:
                s += f"(if {cond} {{ {'; '.join(str(stmt) for stmt in block)} }})"
            else:
                s += f" elsif {cond} {{ {'; '.join(str(stmt) for stmt in block)} }}"
        if self.else_branch:
            s += f" else {{ {'; '.join(str(stmt) for stmt in self.else_branch)} }}"
        return s



# Handles simple if-else statements (without elsif)
class If(Expression):
    def __init__(self, condition: Expression, then_branch: List[Expression], else_branch: List[Expression] = None):
        self.condition = condition              # The condition to evaluate (must return a boolean)
        self.then_branch = then_branch          # List of statements to execute if the condition is true
        self.else_branch = else_branch          # Optional list of statements if the condition is false

    def evaluate(self, env, verbose=True):
        cond_value = self.condition.evaluate(env, verbose)  # Evaluate the condition expression

        # Ensure the condition evaluates to a boolean
        if not isinstance(cond_value, bool):
            raise TypeError("Condition in 'if' must evaluate to a Boolean.")

        if cond_value:
            # If condition is true, execute then-branch in a new local environment
            local_env = Environment(env)
            result = None
            for stmt in self.then_branch:
                result = stmt.evaluate(local_env, verbose)  # Execute each statement in the then-branch
            return result
        elif self.else_branch is not None:
            # If condition is false and there's an else-branch, execute it
            local_env = Environment(env)
            result = None
            for stmt in self.else_branch:
                result = stmt.evaluate(local_env, verbose)  # Execute each statement in the else-branch
            return result

        return None  # If no condition matched and no else-branch, return nothing

    def __str__(self) -> str:
        # Create string representation of the if-else structure
        else_part = f" else {{ {'; '.join(str(stmt) for stmt in self.else_branch)} }}" if self.else_branch else ""
        return f"(if {self.condition} {{ {'; '.join(str(stmt) for stmt in self.then_branch)} }}{else_part})"



# Represents a block of statements enclosed in braces { }
# Used for scopes in if, while, functions, etc.
class Block(Expression):
    def __init__(self, statements: List[Expression]):
        self.statements = statements  # List of expressions/statements in the block

    def evaluate(self, env, verbose=True):
        result = None
        local_env = Environment(env)  # Create a new local scope for the block

        for stmt in self.statements:
            try:
                result = stmt.evaluate(local_env, verbose)
            except ReturnException as ret:
                return ret.value  # Return immediately on return

        return result  # Return result of last statement if no return

    def __str__(self):
        return "\n".join(str(stmt) for stmt in self.statements)


# Handles while loops like: while (condition) { ... }
class While(Expression):
    def __init__(self, condition: Expression, body: List[Expression]):
        self.condition = condition  # Expression to evaluate before each loop iteration
        self.body = body  # List of statements to execute in the loop body

    def evaluate(self, env, verbose=True):
        result = None
        while True:
            local_env = Environment(env)  # New scope for each iteration (ensures block-local variables)
            cond_value = self.condition.evaluate(local_env, verbose)

            if not isinstance(cond_value, bool):
                raise TypeError("While condition must evaluate to boolean.")

            if not cond_value:
                break  # Exit the loop if condition is false

            for stmt in self.body:
                result = stmt.evaluate(local_env, verbose)  # Execute loop body

        return result  # Return result of the last body execution (or None if loop never ran)

    def __str__(self) -> str:
        return f"(while {self.condition} {{ {'; '.join(str(stmt) for stmt in self.body)} }})"


# Converts a value to a float using float() built-in function
class ToFloat(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression  # The expression whose value we want to convert

    def evaluate(self, env, verbose=True):
        value = self.expression.evaluate(env, verbose)
        try:
            return float(value)  # Attempt conversion to float
        except ValueError:
            raise TypeError(f"Cannot convert to float: {value}")

    def __str__(self) -> str:
        return f"(float {self.expression})"


# Converts a value to a string using str() built-in function
class ToString(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression  # The expression whose value we want to convert

    def evaluate(self, env, verbose=True):
        value = self.expression.evaluate(env, verbose)
        try:
            return str(value)  # Attempt conversion to string
        except Exception:
            raise TypeError(f"Cannot convert to string: {value}")

    def __str__(self):
        return f"(str {self.expression})"


    

# Handles 'for' loops like: for (i = 0; i < 10; i = i + 1) { ... }
class For(Expression):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer  # The initial assignment (e.g., i = 0)
        self.condition = condition      # The loop condition (e.g., i < 10)
        self.increment = increment      # The increment expression (e.g., i = i + 1)
        self.body = body                # List of statements to execute in each iteration

    def evaluate(self, env, verbose=True):
        # Make sure initializer is an assignment (e.g., i = 0)
        if not isinstance(self.initializer, Assignment):
            raise TypeError("For loop initializer must be an assignment.")

        loop_var_name = self.initializer.name.lexeme  # Get the name of the loop variable

        loop_env = Environment(env)  # Create a new local environment for the loop

        # Define the loop variable in the loop's environment using its evaluated value
        loop_env.define(loop_var_name, self.initializer.value_expr.evaluate(env, verbose))

        while True:
            # Evaluate the loop condition in the current loop environment
            cond = self.condition.evaluate(loop_env, verbose)
            if not isinstance(cond, bool):
                raise TypeError("For loop condition must be a boolean.")

            if not cond:
                break  # Exit the loop when condition becomes false

            # Create a new nested environment for the body in each iteration
            body_env = Environment(loop_env)

            # Evaluate all statements in the loop body
            for stmt in self.body:
                stmt.evaluate(body_env, verbose)

            # Apply the increment expression after executing the body
            self.increment.evaluate(loop_env, verbose)

    def __str__(self):
        return f"(for {self.initializer}; {self.condition}; {self.increment} {{ {'; '.join(str(stmt) for stmt in self.body)} }})"


# Handles function declarations like:
# fun greet(name) { print "Hello, ", name }
class Function(Expression):
    def __init__(self, name: str, param_names: list[str], body: List[Expression]):
        self.name = name                      # Name of the function
        self.param_names = param_names        # List of parameter names
        self.body = body                      # List of statements in the function body

    def evaluate(self, env, verbose=True):
        # Store the function in the current environment using its name
        env.define(self.name, self)
        return None

    def call(self, args: list, calling_env, verbose=True):
        # Validate argument count
        if len(args) != len(self.param_names):
            raise TypeError(f"Function '{self.name}' expects {len(self.param_names)} arguments, got {len(args)}.")

        # Create a local scope/environment for the function execution
        local_env = Environment(calling_env)

        # Bind argument values to parameter names in the local environment
        for name, value in zip(self.param_names, args):
            local_env.define(name, value)

        try:
            result = None
            # Evaluate each statement in the function body
            for stmt in self.body:
                result = stmt.evaluate(local_env, verbose)
            return result
        # If a return statement was hit, return its value
        except ReturnException as ret:
            return ret.value

    def __str__(self):
        return f"<function {self.name}({', '.join(self.param_names)})>"


# Handles function calls like: greet("Fanis")
class FunctionCall(Expression):
    def __init__(self, callee: Expression, arguments: list[Expression]):
        self.callee = callee          # The function or class to be called
        self.arguments = arguments    # List of argument expressions passed to it

    def evaluate(self, env, verbose=True):
        # Evaluate the function being called (could be user-defined function or class)
        target = self.callee.evaluate(env, verbose)

        # Evaluate all argument expressions before passing
        arg_values = [arg.evaluate(env, verbose) for arg in self.arguments]

        # If it's a user-defined function, call it
        if isinstance(target, Function):
            return target.call(arg_values, env, verbose)

        # If it's a class, instantiate it (no args supported for now)
        if isinstance(target, ClassDefinition):
            if len(arg_values) > 0:
                raise TypeError(f"Class '{target.name}' does not accept arguments (yet)")
            return target.instantiate(env, verbose)

        # If it's not callable, raise an error
        raise TypeError(f"'{self.callee}' is not a callable function or class")

    def __str__(self):
        return f"{self.callee}({', '.join(str(arg) for arg in self.arguments)})"

    

#Handles return statements inside functions
class Return(Expression):
    def __init__(self, value_expr):
        self.value_expr = value_expr  # The expression to return

    def evaluate(self, env, verbose=True):
        if self.value_expr is None:
            raise ReturnException(None)
        value = self.value_expr.evaluate(env, verbose)
        raise ReturnException(value)



#This custom exception is used to break out of a function early when a return is hit
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value  # The value being returned


#Handles list literals like [1, 2, 3]
class ListLiteral(Expression):
    def __init__(self, elements: List[Expression]):
        self.elements = elements  # Store the list of element expressions

    def evaluate(self, env, verbose=True):
        # Evaluate each element and return the fully evaluated list
        return [el.evaluate(env, verbose) for el in self.elements]

    def __str__(self):
        return "[" + ", ".join(str(el) for el in self.elements) + "]"

# Handles accessing elements from a list by index like arr[0]
class IndexAccess(Expression):
    def __init__(self, collection_expr, index_expr):
        self.collection_expr = collection_expr  # Expression that evaluates to a list
        self.index_expr = index_expr  # Expression that evaluates to an index

    def evaluate(self, env, verbose=True):
        collection = self.collection_expr.evaluate(env, verbose)  # Evaluate the list
        index = self.index_expr.evaluate(env, verbose)  # Evaluate the index

        if not isinstance(collection, list):
            raise TypeError("Indexing is only supported on lists.")  # Must be a list

        if not isinstance(index, (int, float)):
            raise TypeError("List index must be a number.")  # Must be int or float (converted later)

        index = int(index)  # Convert float to int if needed

        if index < 0 or index >= len(collection):
            raise IndexError("List index out of bounds.")  # Prevent out-of-range access

        return collection[index]  # Return the value at the index

    def __str__(self):
        return f"{self.collection_expr}[{self.index_expr}]"  # ToString format for debug printing


# Handles class declarations like:
# class Dog { name = "Rex" age = 5 }
class Class(Expression):
    def __init__(self, name: str, body: list):
        self.name = name
        self.body = body  # list of statements (typically assignments) inside the class body

    def evaluate(self, env, verbose=True):
        class_def = ClassDefinition(self.name, self.body)  # Wrap the body into a ClassDefinition object
        env.define(self.name, class_def)  # Store class definition in current environment
        return None

    def __str__(self):
        return f"<class {self.name}>"  # For debugging: display class name


# Represents the compiled definition of a class after evaluation
class ClassDefinition:
    def __init__(self, name, body):
        self.name = name  # Class name
        self.body = body  # Body is the list of assignments for fields

    def instantiate(self, env, verbose=True):
        instance = Instance()  # Create a new instance of the class
        for stmt in self.body:
            if isinstance(stmt, Assignment):  # Only assign values for field definitions
                value = stmt.value_expr.evaluate(env, verbose)
                instance.fields[stmt.name.lexeme] = value  # Store field in instance
        return instance  # Return the created instance


# Represents an instance of a class (object) with its own fields
class Instance:
    def __init__(self):
        self.fields = {}  # Dictionary to store instance variables

    def get(self, name):
        if name in self.fields:
            return self.fields[name]  # Return the value if the field exists
        raise NameError(f"Undefined field '{name}'")  # Raise error for unknown field

    def __str__(self):
        return f"<instance {self.fields}>"  # Debug display of instance contents


# Handles access to fields of an instance (e.g., obj.name)
class GetField(Expression):
    def __init__(self, object_expr: Expression, field_name: Token):
        self.object_expr = object_expr  # Expression resolving to the instance (e.g., 'd')
        self.field_name = field_name    # Token representing the field being accessed (e.g., 'age')

    def evaluate(self, env, verbose=True):
        obj = self.object_expr.evaluate(env, verbose)  # Evaluate object expression
        if isinstance(obj, Instance):  # Ensure it's an instance
            return obj.get(self.field_name.lexeme)  # Retrieve the field value
        raise TypeError("Only instances have fields")  # Disallow field access on non-objects

    def __str__(self):
        return f"{self.object_expr}.{self.field_name.lexeme}"  # Display access as e.g. d.age


# Handles setting a field value on an object (e.g., obj.name = "value")
class SetField(Expression):
    def __init__(self, object_expr: Expression, field_name: Token, value_expr: Expression):
        self.object_expr = object_expr  # The instance to modify
        self.field_name = field_name    # Token representing the field name to set
        self.value_expr = value_expr    # Expression that evaluates to the value being assigned

    def evaluate(self, env, verbose=True):
        obj = self.object_expr.evaluate(env, verbose)  # Evaluate the object
        if not isinstance(obj, Instance):
            raise TypeError("Only instances have fields")  # Must be an object instance

        value = self.value_expr.evaluate(env, verbose)  # Evaluate the value expression
        obj.fields[self.field_name.lexeme] = value  # Set the field value
        return value  # Return the value for assignment chaining or consistency

    def __str__(self):
        return f"{self.object_expr}.{self.field_name.lexeme} = {self.value_expr}"  # e.g., d.age = 10



