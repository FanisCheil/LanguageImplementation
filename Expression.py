from abc import ABC, abstractmethod 
from Token import Token, TokenType
from typing import List


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
        if self.name.lexeme not in env:
            raise NameError(f"Undefined variable '{self.name.lexeme}'")
        return env[self.name.lexeme]
    
    def __str__(self) -> str:
        return f"{self.name.lexeme}"

#Handles variable assignments like `x = 5`
class Assignment(Expression):
    def __init__(self, name: Token, value_expr: Expression):
        self.name = name
        self.value_expr = value_expr

    def evaluate(self, env, verbose=True):
        value = self.value_expr.evaluate(env, verbose)
        env[self.name.lexeme] = value
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
                last_value = None
                for stmt in block:
                    last_value = stmt.evaluate(env, verbose)
                return last_value  #  Return the final statement's result

        if self.else_branch:
            if verbose:
                print("[DEBUG] No condition matched. Executing else branch.")
            last_value = None
            for stmt in self.else_branch:
                last_value = stmt.evaluate(env, verbose)
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
            result = None
            for stmt in self.then_branch:
                result = stmt.evaluate(env, verbose)
            return result
        elif self.else_branch is not None:
            result = None
            for stmt in self.else_branch:
                result = stmt.evaluate(env, verbose)
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
        for stmt in self.statements:
            result = stmt.evaluate(env, verbose)
        return result

    def __str__(self):
        return "\n".join(str(stmt) for stmt in self.statements)

class While(Expression):
    def __init__(self, condition: Expression, body: List[Expression]):
        self.condition = condition
        self.body = body

    def evaluate(self, env, verbose=True):
        result = None  # Track result of last executed statement
        while True:
            cond_value = self.condition.evaluate(env, verbose)

            if not isinstance(cond_value, bool):
                raise TypeError("While condition must evaluate to boolean.")

            if not cond_value:
                break

            for stmt in self.body:
                result = stmt.evaluate(env, verbose)

        return result  # ← This allows outer expression (like Block or If) to print the result

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
    

class For(Expression):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def evaluate(self, env, verbose=True):
        if self.initializer:
            self.initializer.evaluate(env, verbose)

        while True:
            cond = self.condition.evaluate(env, verbose)
            if not isinstance(cond, bool):
                raise TypeError("For loop condition must be a boolean.")

            if not cond:
                break

            for stmt in self.body:
                stmt.evaluate(env, verbose)

            if self.increment:
                self.increment.evaluate(env, verbose)

    def __str__(self):
        return f"(for {self.initializer}; {self.condition}; {self.increment} {{ {'; '.join(str(stmt) for stmt in self.body)} }})"
