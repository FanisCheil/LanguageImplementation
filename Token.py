from enum import Enum

class TokenType(Enum):
    # Single character tokens
    LEFT_PAREN = 0
    RIGHT_PAREN = 1
    PLUS = 2
    MINUS = 3
    TIMES = 4
    DIV = 5
    MOD = 6
    EXP = 7
    NEWLN = 8 

    # Literals
    FLOAT = 20  # Numbers
    STRING = 21  # Text inside quotes
    
    EOF = 100  # End of input

class Token:
    def __init__(
            self,
            type: TokenType,
            lexeme: str,
            literal: object,
            line: int,
            col: int,
        ) -> None:
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line
        self.col: int = col

    def __str__(self) -> str:
        return f"<Token {self.type.name}, '{self.lexeme}', {self.literal}, line {self.line}, col {self.col}>"
