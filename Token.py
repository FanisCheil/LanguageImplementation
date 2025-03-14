from enum import Enum

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = 0 # (
    RIGHT_PAREN = 1 # )
    PLUS = 2 # +
    MINUS = 3 # -
    TIMES = 4 # *
    DIV = 5 # /
    MOD = 6 # %
    EXP = 7 # **
    NEWLN = 8 
    BANG = 9  # !
    EQUAL_EQUAL = 10  # ==
    BANG_EQUAL = 11  # !=
    LESS = 12  # <
    LESS_EQUAL = 13  # <=
    GREATER = 14  # >
    GREATER_EQUAL = 15  # >=
    AND = 16  # and
    OR = 17  # or
    
    # Literals
    FLOAT = 18  # Numbers
    STRING = 19  # Text inside quotes
    BOOLEAN = 20  # true, false
    EQUAL = 21 # =
    EOF = 100  # End of input

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int, col: int) -> None:
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line
        self.col: int = col

    def __str__(self) -> str:
        return f"<Token {self.type.name}, '{self.lexeme}', {self.literal}, line {self.line}, col {self.col}>"
