from abc import ABC, abstractmethod 
from Token import Token, TokenType
from typing import List
from Environment import Environment
from typing import Optional


#Parent class for all expression types
class Expression(ABC):
    @abstractmethod #This forces all subclasses to implement the evaluate() function
    def evaluate(self, env, verbose=True): #Method which evaluates the expression
        pass

#Handles operations like 5 + 3, true and false, etc.
class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
        self.left = left #The left operand(another expression)
        self.operator = operator #The operator(+,-,*,/,or,etc.)
        self.right = right #The right operand(another expression)

    def evaluate(self, env, verbose=True):
         #recurcively call evaluate() on left and right, ensuring the entire tree is resolved
        left_value = self.left.evaluate(env, verbose)
        right_value = self.right.evaluate(env, verbose)

        
        if verbose:
            print(f"Evaluating: {left_value} {self.operator.lexeme} {right_value}")


        #Ensure both operands are booleans before performing logical operations(and, or)
        #If not return and error message
        if self.operator.type == TokenType.AND:
            if isinstance(left_value, bool) and isinstance(right_value, bool):
                return left_value and right_value 
            raise TypeError(f"Cannot use 'and' between {type(left_value).__name__} and {type(right_value).__name__}.")
        elif self.operator.type == TokenType.OR:
            if isinstance(left_value, bool) and isinstance(right_value, bool):
                return left_value or right_value
            raise TypeError(f"Cannot use 'or' between {type(left_value).__name__} and {type(right_value).__name__}.")

        #Checks if two valus are equal
        if self.operator.type == TokenType.EQUAL_EQUAL:
            return left_value == right_value
                # 5 == 5 , 
                # "hello" == "hello", 
                # ((5 + 5) == 10) == ("helloworld" == ("hello" + "world"))
                # 5 == 3


        #Check if two values are not equal
        elif self.operator.type == TokenType.BANG_EQUAL:
            return left_value != right_value
        
        #Ensure comparizons only happen between numbers for operator <, <=, >, >=, otherwise return an error
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

       
        if self.operator.type == TokenType.PLUS:
            #string concatenation
            if isinstance(left_value, str) and isinstance(right_value, str):
                return left_value + right_value
                # "hello" + "world" -> "helloworld"
            
            #number addition
            elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value + right_value 
                # 5 + 3 -> 8

                # list concatenation
            elif isinstance(left_value, list) and isinstance(right_value, list):
                return left_value + right_value

              
            #Prevent invlalid operations like "hello" + 5 -> error message
            else:
                raise TypeError(f"Cannot use '+' between {type(left_value).__name__} and {type(right_value).__name__}.")

        #Ensures that only numeric types are user for -, *, /, %, **
        if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
            raise TypeError(f"Invalid operation: Cannot use '{self.operator.lexeme}' between {type(left_value).__name__} and {type(right_value).__name__}.")
        
        #Basic math operations
        if self.operator.type == TokenType.MINUS:
            return left_value - right_value
        elif self.operator.type == TokenType.TIMES:
            return left_value * right_value
        elif self.operator.type == TokenType.DIV:
            #Handle division by zero
            if right_value == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left_value / right_value
        elif self.operator.type == TokenType.MOD:
            return left_value % right_value
        elif self.operator.type == TokenType.EXP:
            # Prevent overflow
            if abs(left_value) > 999 or abs(right_value) > 999:
                raise OverflowError("Number too large to compute.")
            return left_value ** right_value
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

#Handles variable references like `x`
class Variable(Expression):
    def __init__(self, name: Token):
        self.name = name

    def evaluate(self, env, verbose=True):
        return env.get(self.name.lexeme)
    
    def __str__(self) -> str:
        return f"{self.name.lexeme}"

#Handles variable assignments like `x = 5`
class Assignment(Expression):
    def __init__(self, name: Token, value_expr: Expression):
        self.name = name
        self.value_expr = value_expr

    def evaluate(self, env, verbose=True):
        value = self.value_expr.evaluate(env, verbose)
        if self.name.lexeme in env:
            env.assign(self.name.lexeme, value)  # αν υπάρχει, ενημέρωσέ τη
        else:
            env.define(self.name.lexeme, value)  # αλλιώς, δημιούργησέ τη
        return value
    
    def __str__(self) -> str:
        return f"(assign {self.name.lexeme} = {self.value_expr})"

#Handles print statements like `print x`
class Print(Expression):
    def __init__(self, expressions: List[Expression]):
        self.expressions = expressions

    def evaluate(self, env, verbose=True):
        result = ""
        for expr in self.expressions:
            value = expr.evaluate(env, verbose)
            result += str(value)
        print(result)
        return None

class Ask(Expression):
    def __init__(self, prompt_expr: Expression):
        self.prompt_expr = prompt_expr  # The expression to display as a prompt

    def evaluate(self, env, verbose=True):
        prompt = self.prompt_expr.evaluate(env, verbose)
        if not isinstance(prompt, str):
            raise TypeError("ask expects a string prompt")
        return input(prompt).strip()

    def __str__(self) -> str:
        return f"(ask {self.prompt_expr})"


class IfChain(Expression):
    def __init__(self, conditions: list, else_branch: list = None):
        self.conditions = conditions
        self.else_branch = else_branch

    def evaluate(self, env, verbose=True):
        for idx, (condition, block) in enumerate(self.conditions):
            result = condition.evaluate(env, verbose)

            if not isinstance(result, bool):
                raise TypeError("Condition must evaluate to boolean.")

            if result:
                local_env = Environment(env)
                last_value = None
                for stmt in block:
                    last_value = stmt.evaluate(local_env, verbose)
                return last_value  #  Return the final statement's result

        if self.else_branch:
            if verbose:
                print("[DEBUG] No condition matched. Executing else branch.")
            local_env = Environment(env)
            last_value = None
            for stmt in self.else_branch:
                last_value = stmt.evaluate(local_env, verbose)
            return last_value  #  Return final else result too

        return None  # If nothing runs


    def __str__(self):
        s = ""
        for i, (cond, block) in enumerate(self.conditions):
            if i == 0:
                s += f"(if {cond} {{ {'; '.join(str(stmt) for stmt in block)} }})"
            else:
                s += f" elsif {cond} {{ {'; '.join(str(stmt) for stmt in block)} }}"
        if self.else_branch:
            s += f" else {{ {'; '.join(str(stmt) for stmt in self.else_branch)} }}"
        return s


class If(Expression):
    def __init__(self, condition: Expression, then_branch: List[Expression], else_branch: List[Expression] = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def evaluate(self, env, verbose=True):
        cond_value = self.condition.evaluate(env, verbose)

        if not isinstance(cond_value, bool):
            raise TypeError("Condition in 'if' must evaluate to a Boolean.")

        if cond_value:
            local_env = Environment(env)
            result = None
            for stmt in self.then_branch:
                result = stmt.evaluate(local_env, verbose)
            return result
        elif self.else_branch is not None:
            local_env = Environment(env)
            result = None
            for stmt in self.else_branch:
                result = stmt.evaluate(local_env, verbose)
            return result

        return None

    def __str__(self) -> str:
        else_part = f" else {{ {'; '.join(str(stmt) for stmt in self.else_branch)} }}" if self.else_branch else ""
        return f"(if {self.condition} {{ {'; '.join(str(stmt) for stmt in self.then_branch)} }}{else_part})"
    



class Block(Expression):
    def __init__(self, statements: List[Expression]):
        self.statements = statements

    def evaluate(self, env, verbose=True):
        result = None
        local_env = Environment(env)  # local scope
        for stmt in self.statements:
            result = stmt.evaluate(local_env, verbose)
        return result

    def __str__(self):
        return "\n".join(str(stmt) for stmt in self.statements)

class While(Expression):
    def __init__(self, condition: Expression, body: List[Expression]):
        self.condition = condition
        self.body = body

    def evaluate(self, env, verbose=True):
        result = None
        while True:
            local_env = Environment(env)  # New scope per iteration (like C)
            cond_value = self.condition.evaluate(local_env, verbose)

            if not isinstance(cond_value, bool):
                raise TypeError("While condition must evaluate to boolean.")

            if not cond_value:
                break

            for stmt in self.body:
                result = stmt.evaluate(local_env, verbose)

        return result

    def __str__(self) -> str:
        return f"(while {self.condition} {{ {'; '.join(str(stmt) for stmt in self.body)} }})"



class ToFloat(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def evaluate(self, env, verbose=True):
        value = self.expression.evaluate(env, verbose)
        try:
            return float(value)
        except ValueError:
            raise TypeError(f"Cannot convert to float: {value}")

    def __str__(self) -> str:
        return f"(float {self.expression})"
    
class ToString(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def evaluate(self, env, verbose=True):
        value = self.expression.evaluate(env, verbose)
        try:
            return str(value)
        except Exception:
            raise TypeError(f"Cannot convert to string: {value}")

    def __str__(self):
        return f"(str {self.expression})"

    

class For(Expression):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def evaluate(self, env, verbose=True):
        if not isinstance(self.initializer, Assignment):
            raise TypeError("For loop initializer must be an assignment.")

        loop_var_name = self.initializer.name.lexeme

        loop_env = Environment(env)

        # Assign the loop variable locally WITHOUT modifying global env
        loop_env.define(loop_var_name, self.initializer.value_expr.evaluate(env, verbose))

        while True:
            cond = self.condition.evaluate(loop_env, verbose)
            if not isinstance(cond, bool):
                raise TypeError("For loop condition must be a boolean.")

            if not cond:
                break

            # Create a nested environment for the loop body
            body_env = Environment(loop_env)

            for stmt in self.body:
                stmt.evaluate(body_env, verbose)

            self.increment.evaluate(loop_env, verbose)


    def __str__(self):
        return f"(for {self.initializer}; {self.condition}; {self.increment} {{ {'; '.join(str(stmt) for stmt in self.body)} }})"

class Function(Expression):
    def __init__(self, name: str, param_names: list[str], body: List[Expression]):
        self.name = name
        self.param_names = param_names
        self.body = body

    def evaluate(self, env, verbose=True):
        env.define(self.name, self)
        return None

    def call(self, args: list, calling_env, verbose=True):
        if len(args) != len(self.param_names):
            raise TypeError(f"Function '{self.name}' expects {len(self.param_names)} arguments, got {len(args)}.")

        local_env = Environment(calling_env)
        for name, value in zip(self.param_names, args):
            local_env.define(name, value)

        try:
            result = None
            for stmt in self.body:
                result = stmt.evaluate(local_env, verbose)
            return result
        except ReturnException as ret:
            return ret.value

    def __str__(self):
        return f"<function {self.name}({', '.join(self.param_names)})>"


class FunctionCall(Expression):
    def __init__(self, callee: Expression, arguments: list[Expression]):
        self.callee = callee
        self.arguments = arguments

    def evaluate(self, env, verbose=True):
        target = self.callee.evaluate(env, verbose)
        arg_values = [arg.evaluate(env, verbose) for arg in self.arguments]

        if isinstance(target, Function):
            return target.call(arg_values, env, verbose)

        
        if isinstance(target, ClassDefinition):
            if len(arg_values) > 0:
                raise TypeError(f"Class '{target.name}' does not accept arguments (yet)")
            return target.instantiate(env, verbose)

        raise TypeError(f"'{self.callee}' is not a callable function or class")

    def __str__(self):
        return f"{self.callee}({', '.join(str(arg) for arg in self.arguments)})"

    

class Return(Expression):
    def __init__(self, value_expr):
        self.value_expr = value_expr

    def evaluate(self, env, verbose=True):
        value = self.value_expr.evaluate(env, verbose)
        raise ReturnException(value)

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class ListLiteral(Expression):
    def __init__(self, elements: List[Expression]):
        self.elements = elements

    def evaluate(self, env, verbose=True):
        return [el.evaluate(env, verbose) for el in self.elements]

    def __str__(self):
        return "[" + ", ".join(str(el) for el in self.elements) + "]"

class IndexAccess(Expression):
    def __init__(self, collection_expr, index_expr):
        self.collection_expr = collection_expr
        self.index_expr = index_expr

    def evaluate(self, env, verbose=True):
        collection = self.collection_expr.evaluate(env, verbose)
        index = self.index_expr.evaluate(env, verbose)

        if not isinstance(collection, list):
            raise TypeError("Indexing is only supported on lists.")

        if not isinstance(index, (int, float)):
            raise TypeError("List index must be a number.")

        index = int(index)

        if index < 0 or index >= len(collection):
            raise IndexError("List index out of bounds.")

        return collection[index]

    def __str__(self):
        return f"{self.collection_expr}[{self.index_expr}]"


class Class(Expression):
    def __init__(self, name: str, body: list):
        self.name = name
        self.body = body  # list of assignments

    def evaluate(self, env, verbose=True):
        class_def = ClassDefinition(self.name, self.body)
        env.define(self.name, class_def)
        return None

    def __str__(self):
        return f"<class {self.name}>"


class ClassDefinition:
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def instantiate(self, env, verbose=True):
        instance = Instance()
        for stmt in self.body:
            if isinstance(stmt, Assignment):
                value = stmt.value_expr.evaluate(env, verbose)
                instance.fields[stmt.name.lexeme] = value
        return instance


class Instance:
    def __init__(self):
        self.fields = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        raise NameError(f"Undefined field '{name}'")

    def __str__(self):
        return f"<instance {self.fields}>"


class GetField(Expression):
    def __init__(self, object_expr: Expression, field_name: Token):
        self.object_expr = object_expr
        self.field_name = field_name

    def evaluate(self, env, verbose=True):
        obj = self.object_expr.evaluate(env, verbose)
        if isinstance(obj, Instance):
            return obj.get(self.field_name.lexeme)
        raise TypeError("Only instances have fields")

    def __str__(self):
        return f"{self.object_expr}.{self.field_name.lexeme}"
    

class SetField(Expression):
    def __init__(self, object_expr: Expression, field_name: Token, value_expr: Expression):
        self.object_expr = object_expr
        self.field_name = field_name
        self.value_expr = value_expr

    def evaluate(self, env, verbose=True):
        obj = self.object_expr.evaluate(env, verbose)
        if not isinstance(obj, Instance):
            raise TypeError("Only instances have fields")

        value = self.value_expr.evaluate(env, verbose)
        obj.fields[self.field_name.lexeme] = value
        return value

    def __str__(self):
        return f"{self.object_expr}.{self.field_name.lexeme} = {self.value_expr}"


