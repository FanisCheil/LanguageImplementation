from abc import ABC, abstractmethod 
from Token import Token, TokenType

#Parent class for all expression types
class Expression(ABC):
    @abstractmethod #This forces all subclasses to implement the evaluate() function
    def evaluate(self): #Method which evaluates the expression
        pass

#Handles operations like 5 + 3, true and false, etc.
class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
        self.left = left #The left operand(another expression)
        self.operator = operator #The operator(+,-,*,/,or,etc.)
        self.right = right #The right operand(another expression)

    def evaluate(self):
         #recurcively call evaluate() on left and right, ensuring the entire tree is resolved
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()

        debug_message = f"Evaluating: {left_value} {self.operator.lexeme} {right_value}"
        print(f"{debug_message}")

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

    def evaluate(self):
        operand_value = self.operand.evaluate() # recursively evaluate the operand before applying the unary operation

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
    def evaluate(self):
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
    def evaluate(self):
        return self.expression.evaluate()

    def __str__(self) -> str:
        return f"(group {self.expression})"
