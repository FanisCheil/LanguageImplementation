from Token import Token, TokenType
from Expression import *
from typing import List

class AST:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self._current = 0  
        self.tree = self._expression()

    def evaluate(self):
        return self.tree.evaluate()

    def _match(self, *types: List[TokenType]) -> bool:
        while self._check(TokenType.NEWLN):  # Skip newline tokens
            self._advance()
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _check(self, type: TokenType) -> bool:
        if self._at_end():
            return False
        return self._peek().type == type

    def _peek(self) -> Token:
        return self.tokens[self._current]
    
    def _advance(self) -> Token:
        next_token = self._peek()
        if not self._at_end():
            self._current += 1
        return next_token

    def _previous(self) -> Token:
        return self.tokens[self._current - 1]

    def _at_end(self):
        return self._peek().type == TokenType.EOF

    def _expression(self):
        expression = self._term()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            if self._at_end():  # If the next expected token is EOF, it's an error
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._term()
            expression = Binary(expression, operator, right)
        return expression
    
    def _term(self):
        expression = self._factor()
        while self._match(TokenType.DIV, TokenType.TIMES, TokenType.MOD ):
            if self._at_end():  # ✅ Prevents missing operand errors
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._factor()
            expression = Binary(expression, operator, right)
        return expression

    def _factor(self):
        expression = self._unary()
        while self._match(TokenType.EXP):
            operator = self._previous()
            right = self._unary()
            expression = Binary(expression, operator, right)
        return expression

    def _unary(self):
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._primary()

    def _primary(self):
        if self._match(TokenType.FLOAT):
            return Literal(self._previous().literal)
        if self._match(TokenType.STRING):  # ✅ Handle string literals
            return Literal(self._previous().literal)
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError("Missing closing parenthesis ')'")  
            return Grouping(expression)
        raise SyntaxError(f"Unexpected token: '{self._peek().lexeme}' at line {self._peek().line}, column {self._peek().col}")
