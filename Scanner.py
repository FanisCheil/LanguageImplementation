from Token import Token, TokenType
from typing import List

class Scanner:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: list[Token] = []
        self._line: int = 1
        self._col: int = 1
        self._cur_char_index: int = 0
        self._cur_char: str = ""

    def advance(self) -> str:
        if self._cur_char_index == len(self.source):
            return ""  
        self._cur_char = self.source[self._cur_char_index]
        self._cur_char_index += 1
        self._col += 1
        return self._cur_char

    def peek(self) -> str:
        if self._cur_char_index == len(self.source):
            return ""  
        return self.source[self._cur_char_index]

    def _scan_float(self) -> None:
        fl = self._cur_char
        while self.peek().isdigit() or self.peek() == ".":
            fl += self.advance()
        self.tokens.append(Token(TokenType.FLOAT, fl, float(fl), self._line, self._col))

    def _scan_string(self) -> None:
        string_value = ""
        while self.peek() != '"' and self.peek() != "":
            string_value += self.advance()
        if self.peek() == "":
            raise SyntaxError("Unterminated string literal")
        self.advance()
        self.tokens.append(Token(TokenType.STRING, string_value, string_value, self._line, self._col))

    def _scan_newline(self) -> None:
        self.tokens.append(Token(TokenType.NEWLN, "\\n", None, self._line, self._col))
        self._line += 1
        self._col = 1

    def scan_tokens(self) -> List[Token]:
        while (c := self.advance()) != "": 
            if c.isspace():  # ✅ Skip whitespace properly
                continue
            elif c == "+":
                self.tokens.append(Token(TokenType.PLUS, c, None, self._line, self._col))
            elif c == "-":
                self.tokens.append(Token(TokenType.MINUS, c, None, self._line, self._col))
            elif c == "*" and self.peek() == "*":
                self.advance()  
                self.tokens.append(Token(TokenType.EXP, "**", None, self._line, self._col))
            elif c == "*":
                self.tokens.append(Token(TokenType.TIMES, c, None, self._line, self._col))
            elif c == "/":
                self.tokens.append(Token(TokenType.DIV, c, None, self._line, self._col))
            elif c == "%":
                self.tokens.append(Token(TokenType.MOD, c, None, self._line, self._col))
            elif c == "(":
                self.tokens.append(Token(TokenType.LEFT_PAREN, c, None, self._line, self._col))
            elif c == ")":
                self.tokens.append(Token(TokenType.RIGHT_PAREN, c, None, self._line, self._col))
            elif c.isdigit():
                self._scan_float()
            elif c == '"':
                self._scan_string()
            elif c == "\n":
                self._scan_newline()
            else:  
                raise SyntaxError(f"Unexpected token: '{c}' at line {self._line}, column {self._col}")

        self.tokens.append(Token(TokenType.EOF, "", None, self._line, self._col))
        return self.tokens
