from abc import ABC, abstractmethod
from Token import Token, TokenType

class Expression(ABC):
    @abstractmethod
    def evaluate(self):
        pass

class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self):
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()

        debug_message = f"Evaluating: {left_value} {self.operator.lexeme} {right_value}"
        print(f"{debug_message}")

        # Handle string concatenation separately
        if self.operator.type == TokenType.PLUS:
            if isinstance(left_value, str) and isinstance(right_value, str):
                return left_value + right_value  
            elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value + right_value  
            else:
                raise TypeError(f"Cannot use '+' between {type(left_value).__name__} and {type(right_value).__name__}.")

        # Ensure both operands are numbers before performing arithmetic
        if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
            raise TypeError(f"Invalid operation: Cannot use '{self.operator.lexeme}' between {type(left_value).__name__} and {type(right_value).__name__}.")

        if self.operator.type == TokenType.MINUS:
            return left_value - right_value
        elif self.operator.type == TokenType.TIMES:
            return left_value * right_value
        elif self.operator.type == TokenType.DIV:
            if right_value == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left_value / right_value
        elif self.operator.type == TokenType.MOD:  
            return left_value % right_value
        elif self.operator.type == TokenType.EXP:
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
        operand_value = self.operand.evaluate()

        # Ensure unary minus is only applied to numbers
        if not isinstance(operand_value, (int, float)):
            raise TypeError(f"Invalid unary operation: Cannot apply '{self.operator.lexeme}' to {type(operand_value).__name__}.")

        if self.operator.type == TokenType.MINUS:
            return -operand_value
        return operand_value  

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.operand})"

class Literal(Expression):
    def __init__(self, value: object) -> None:
        self.value = value

    def evaluate(self):
        # Handle both string and numeric literals
        if isinstance(self.value, (int, float, str)):
            return self.value
        raise TypeError(f"Invalid literal: Expected number or string but got {type(self.value).__name__}.")

    def __str__(self) -> str:
        return f"{self.value}"

class Grouping(Expression):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def evaluate(self):
        return self.expression.evaluate()

    def __str__(self) -> str:
        return f"(group {self.expression})"
