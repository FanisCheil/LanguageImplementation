from Token import Token, TokenType
from Expression import *
from typing import List

class AST:
    #Initialize the AST
    def __init__(self, tokens: List[Token]): #Takes a list of tokens from the scanner as input
        self.tokens = tokens #Stores the token list
        self._current = 0  #track the current position in the token list
        self.tree = self._expression() #Parses the expression by calling _expression(), which builds the AST
        #The final tree structure is stored in self.tree

    def evaluate(self):
        return self.tree.evaluate() #Call the evaluate() on the root node (self.tree), which recursively evaluates the enitre AST
    
    #Checks if the next token matches a given type
    def _match(self, *types: List[TokenType]) -> bool:

        #Skip newlines so that expressions arent affected by line breaks
        while self._check(TokenType.NEWLN):  
            self._advance()

        #Loop through the provided token types
        
        for type in types:
            if self._check(type): #If the token matches on of them   
                self._advance() #Consume the token
                return True #Return true to indicate a match
        return False #if no match is found return false

    #Peek at the curnent toekn without consume it
    def _check(self, type: TokenType) -> bool: #Take a TokenType

        if self._at_end(): #if end of input is reached return false
            return False
        
        #Otherwise, check if the current toekn matches the given type
        return self._peek().type == type
    
    #Return the current token without consume it
    def _peek(self) -> Token:
        return self.tokens[self._current]
    
    #Moves to the next token and returns it
    def _advance(self) -> Token:

        next_token = self._peek() #Retreives the current token before advancing

        #If not at the end of input then move forward
        if not self._at_end():
            self._current += 1

        #Return the token before advancing
        return next_token
    
    #Returns the last token that was consumed
    def _previous(self) -> Token:
        return self.tokens[self._current - 1]
    
    #Checks if the end of input has been reached
    def _at_end(self):

        #if the next token is EOF return true, Otherwise false
        return self._peek().type == TokenType.EOF
    

    
    #--------------------------------------------------
    #Expression Parsing Functions (Recursive Descent) |
    #--------------------------------------------------
    
    #This is the starting point of parsing
    #_expression() Parses the full expression

    
    def _expression(self):
        return self._logical_or() # Calls _logical_or() which handles boolean or (or) operations
    

    #Handle or boolean expressions
    def _logical_or(self):
        expression = self._logical_and() # Calls _logical_and() to parse the left-hand side
        #until here _logical_and() processes everything before the first "or" operator.
        #this means expression becomes the left-hand side of the "or" expression

        #if "or" ir found
        while self._match(TokenType.OR):
            operator = self._previous() #Store the operator "or"

            right = self._logical_and() #Parse the right-hand side
            #this time, _logical_and() processes everything after or. which becomes the right-hand side.
            expression = Binary(expression, operator, right) #Construct a binary expression
        return expression #Return the complete or expression
    
    #The same for the and boolean operator
    def _logical_and(self):
        expression = self._equality() #Left-hand side
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality() #right-hand side
            expression = Binary(expression, operator, right)
        return expression

    #Handles == , != operators
    def _equality(self):
        expression = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._comparison()
            expression = Binary(expression, operator, right)
        return expression

    #Handles <, <=, >, >= operators
    def _comparison(self):
        expression = self._term()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._term()
            expression = Binary(expression, operator, right)
        return expression
    
    #Handles +, - operators
    def _term(self):
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._factor()
            expression = Binary(expression, operator, right)
        return expression
    

    #Handles /, *, % operators
    def _factor(self):
        expression = self._exponent()
        while self._match(TokenType.DIV, TokenType.TIMES, TokenType.MOD):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._exponent()
            expression = Binary(expression, operator, right)
        return expression
    
    #Handles ** operator
    def _exponent(self):
        expression = self._unary()
        while self._match(TokenType.EXP):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._unary()
            expression = Binary(expression, operator, right)
        return expression
    
    #handles unary operations like -2 * 3 or !true
    def _unary(self):
    # If it is '-', parse the right operand
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        # If it is '!', parse the right operand
        if self._match(TokenType.BANG):
            operator = self._previous()
            right = self._unary()

            # If right is a grouping, evaluate it first
            if isinstance(right, Grouping):
                right = Literal(right.evaluate())

            # Ensure '!' is only used with booleans
            if not isinstance(right, Literal) or not isinstance(right.value, bool):
                raise SyntaxError(f"Syntax Error: '!' must be followed by a Boolean, found '{right}'.")

            return Unary(operator, right)

        return self._primary()


    def _primary(self):

        #if it is a number return it
        if self._match(TokenType.FLOAT):
            if self._check(TokenType.BANG):
                raise SyntaxError(f"Syntax Error: Unexpected token '!' after number.")
            return Literal(self._previous().literal)
        
        #if it is a string return it
        if self._match(TokenType.STRING):  
            return Literal(self._previous().literal)
        
        #if it is a boolen, return it
        if self._match(TokenType.BOOLEAN):  
            return Literal(self._previous().literal)

        #if it is a (, parse the entire inner expression
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()

            #Ensure there is a cosing parenthesis for every opening parenthesis  
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError(
                    f"Syntax Error: Missing closing parenthesis ')' at line {self._peek().line}, column {self._peek().col}."
                )
            
            return Grouping(expression)

        raise SyntaxError(
            f"Unexpected token: '{self._peek().lexeme}' at line {self._peek().line}, column {self._peek().col}."
        )


"""
============================== EXPRESSION PARSING OVERVIEW ==============================

The following functions handle parsing expressions using a **recursive descent parser**. 

Expression parsing follows a **hierarchical structure**, enforcing **operator precedence** 
(from lowest to highest priority):

   
     Expression  →  Logical OR                  
     Logical OR   →  Logical AND  { "or" Logical AND }   (lowest precedence)
     Logical AND  →  Equality  { "and" Equality }        
     Equality     →  Comparison  { ( "==" | "!=" ) Comparison } 
     Comparison   →  Term  { ( ">" | ">=" | "<" | "<=" ) Term } 
     Term        →  Factor  { ( "+" | "-" ) Factor }           
     Factor      →  Exponent { ( "*" | "/" | "%" ) Exponent }  
     Exponent    →  Unary  { "**" Unary }                      
     Unary       →  ( "!" | "-" ) Unary  |  Primary            
     Primary     →  NUMBER | STRING | BOOLEAN | "(" Expression ")" (highest precedence)
   

Recursive descent works **top-down**, calling the **highest precedence function first**.
Each function processes **its part of the expression**, then moves deeper for operators with
higher precedence.

1 **Logical OR (`or`)**  → If found, parse the right side using Logical AND.
2 **Logical AND (`and`)**  → If found, parse the right side using Equality.
3 **Equality (`==`, `!=`)** → If found, parse the right side using Comparison.
4 **Comparison (`<`, `<=`, `>`, `>=`)** → If found, parse the right side using Term.
5 **Term (`+`, `-`)** → If found, parse the right side using Factor.
6 **Factor (`*`, `/`, `%`)** → If found, parse the right side using Exponent.
7 **Exponent (`**`)** → If found, parse the right side using Unary.
8 **Unary (`!`, `-`)** → If found, parse the right side using Primary.
9 **Primary (`NUMBER`, `STRING`, `BOOLEAN`, `(...)`)** → Final values in the expression.
"""

