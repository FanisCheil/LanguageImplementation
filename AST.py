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
        while self._check(TokenType.NEWLN):  
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
        return self._logical_or()

    def _logical_or(self):
        expression = self._logical_and()
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._logical_and()
            expression = Binary(expression, operator, right)
        return expression

    def _logical_and(self):
        expression = self._equality()
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expression = Binary(expression, operator, right)
        return expression

    def _equality(self):
        expression = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._comparison()
            expression = Binary(expression, operator, right)
        return expression


    def _comparison(self):
        expression = self._term()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._term()
            expression = Binary(expression, operator, right)
        return expression
    
    def _term(self):
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._factor()
            expression = Binary(expression, operator, right)
        return expression

    def _factor(self):
        expression = self._exponent()
        while self._match(TokenType.DIV, TokenType.TIMES, TokenType.MOD):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._exponent()
            expression = Binary(expression, operator, right)
        return expression

    def _exponent(self):
        expression = self._unary()
        while self._match(TokenType.EXP):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._unary()
            expression = Binary(expression, operator, right)
        return expression

    def _unary(self):
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        if self._match(TokenType.BANG):
            operator = self._previous()
            right = self._unary()

            
            if not isinstance(right, Literal) or not isinstance(right.value, bool):
                raise SyntaxError(f"Syntax Error: '!' must be followed by a Boolean, found '{right.value}'.")

            return Unary(operator, right)

        return self._primary()

    def _primary(self):
        if self._match(TokenType.FLOAT):
            if self._check(TokenType.BANG):
                raise SyntaxError(f"Syntax Error: Unexpected token '!' after number.")
            return Literal(self._previous().literal)

        if self._match(TokenType.STRING):  
            return Literal(self._previous().literal)

        if self._match(TokenType.BOOLEAN):  
            return Literal(self._previous().literal)

        
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()

            
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError(
                    f"Syntax Error: Missing closing parenthesis ')' at line {self._peek().line}, column {self._peek().col}."
                )
            
            return Grouping(expression)

        raise SyntaxError(
            f"Unexpected token: '{self._peek().lexeme}' at line {self._peek().line}, column {self._peek().col}."
        )




