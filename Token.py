from enum import Enum  

# Define all possible types of tokens in the language
class TokenType(Enum):
    # Single-character tokens (symbols used in expressions)
    LEFT_PAREN = 0        # (
    RIGHT_PAREN = 1       # )
    PLUS = 2              # +
    MINUS = 3             # -
    TIMES = 4             # *
    DIV = 5               # /
    MOD = 6               # %
    EXP = 7               # **
    NEWLN = 8             # Newline (used to separate statements)
    BANG = 9              # !

    # Comparison operators
    EQUAL_EQUAL = 10      # ==
    BANG_EQUAL = 11       # !=
    LESS = 12             # <
    LESS_EQUAL = 13       # <=
    GREATER = 14          # >
    GREATER_EQUAL = 15    # >=

    # Logical operators
    AND = 16              # and
    OR = 17               # or

    # Literals
    FLOAT = 18            # Number literals (e.g., 3.14, 5)
    STRING = 19           # Text in quotes (e.g., "hello")
    BOOLEAN = 20          # true / false

    # Assignment
    EQUAL = 21            # =

    # Identifiers and keywords
    IDENTIFIER = 22       # Variable names or function names
    PRINT = 23            # print keyword
    COMMA = 24            # ,
    ASK = 25              # ask keyword (for user input)

    # Control flow
    IF = 26               # if keyword
    LEFT_BRACE = 27       # {
    RIGHT_BRACE = 28      # }
    ELSE = 29             # else keyword
    ELSIF = 30            # elsif keyword
    WHILE = 31            # while loop keyword
    FOR = 32              # for loop keyword
    SEMICOLON = 33        # ;
    FUN = 34              # fun keyword (function definition)
    RETURN = 35           # return statement
    LEFT_BRACKET = 36     # [ (used for lists or indexing)
    RIGHT_BRACKET = 37    # ]
    CLASS = 38            # class keyword
    DOT = 39              # . (used for object field access)

    # Special token
    EOF = 100             # End of file/input (used to indicate there's nothing more to parse)


# Token class represents a single token in the source code
class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int, col: int) -> None:
        self.type: TokenType = type      # The type of the token (e.g., PLUS, IDENTIFIER)
        self.lexeme: str = lexeme        # The actual string from the source code (e.g., "+", "x", "if")
        self.literal: object = literal   # The actual value for literals (e.g., 5, "hello"), or None
        self.line: int = line            # Line number where the token was found (for error reporting)
        self.col: int = col              # Column number where the token starts (for error context)

    def __str__(self) -> str:
        # Returns a readable representation of the token, used for debugging
        return f"<Token {self.type.name}, '{self.lexeme}', {self.literal}, line {self.line}, col {self.col}>"
