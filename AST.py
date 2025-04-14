from Token import Token, TokenType
from Expression import *
from typing import List

class AST:
    # Initialize the AST
    def __init__(self, tokens: List[Token]):  # Takes a list of tokens from the scanner as input
        self.tokens = tokens  # Stores the token list
        self._current = 0  # track the current position in the token list
        self.variables = {}  # Global variable environment
        self.tree = self._program()
  # Parses a full statement
        # The final tree structure is stored in self.tree

    def evaluate(self, env, verbose=True):
        return self.tree.evaluate(env, verbose)  # Call the evaluate() on the root node (self.tree), which recursively evaluates the entire AST
    
    # Checks if the next token matches a given type
    def _match(self, *types: List[TokenType]) -> bool:
        # Skip newlines so that expressions aren't affected by line breaks
        while self._check(TokenType.NEWLN):  
            self._advance()

        # Loop through the provided token types
        for type in types:
            if self._check(type):  # If the token matches one of them   
                self._advance()  # Consume the token
                return True  # Return true to indicate a match
        return False  # if no match is found return false

    # Peek at the current token without consuming it
    def _check(self, type: TokenType) -> bool:
        if self._at_end():  # if end of input is reached return false
            return False
        
        # Otherwise, check if the current token matches the given type
        return self._peek().type == type

    # Look ahead to the next token
    def _check_next(self, type: TokenType) -> bool:
        if self._current + 1 >= len(self.tokens):
            return False
        return self.tokens[self._current + 1].type == type
    
    # Return the current token without consuming it
    def _peek(self) -> Token:
        return self.tokens[self._current]
    
    # Moves to the next token and returns it
    def _advance(self) -> Token:
        next_token = self._peek()  # Retrieves the current token before advancing
        # If not at the end of input then move forward
        if not self._at_end():
            self._current += 1
        return next_token
    
    # Returns the last token that was consumed
    def _previous(self) -> Token:
        return self.tokens[self._current - 1]
    
    # Checks if the end of input has been reached
    def _at_end(self):
        # if the next token is EOF return true, Otherwise false
        return self._peek().type == TokenType.EOF
    
    def _program(self):
        statements = []
        while not self._at_end():
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
        return Block(statements)
    
     # Check and parse a full statement (print, assignment, or expression)
    
    def _program(self):
        statements = []  # Initialize a list to store top-level statements
        while not self._at_end():  # Keep parsing until all tokens are consumed
            stmt = self._statement()  # Parse a statement
            if stmt is not None:  # Only add non-null statements
                statements.append(stmt)  # Append the parsed statement to the list
        return Block(statements)  # Wrap all statements in a Block node and return

    # Check and parse a full statement (print, assignment, or expression)
    def _statement(self):

        if self._match(TokenType.CLASS):
            return self._class_declaration()  # Parse a class declaration if 'class' keyword is found

        if self._match(TokenType.RETURN):
            return self._return_statement()  # Parse a return statement

        if self._match(TokenType.FUN):
            return self._function_declaration()  # Parse a function declaration

        if self._match(TokenType.FOR):
            return self._for_loop()  # Parse a for-loop

        if self._match(TokenType.WHILE):
            return self._while_statement()  # Parse a while-loop

        # Skip any stray closing braces leftover from block parsing
        if self._match(TokenType.RIGHT_BRACE):
            return None  # Do nothing if we see a lone closing brace

        if self._match(TokenType.PRINT):
            expressions = [self._expression()]  # Start with first expression
            while self._match(TokenType.COMMA):  # support comma-separated expressions
                expressions.append(self._expression())  # Add more expressions after commas
            return Print(expressions)  # Wrap them in a Print node

        if self._match(TokenType.IF):
            return self._if_statement()  # Parse an if-elsif-else block

        # Generic assignment detection for variables and fields
        checkpoint = self._current  # Save the current index in case this is not an assignment
        expr = self._expression()  # Parse an expression (could be a variable, function call, etc.)

        if self._match(TokenType.EQUAL):
            value_expr = self._expression()  # If we see '=', parse the right-hand side
            if isinstance(expr, Variable):  # If the left-hand side is a variable
                return Assignment(expr.name, value_expr)
            if isinstance(expr, GetField):  # If assigning to a class field like obj.x
                return SetField(expr.object_expr, expr.field_name, value_expr)
            raise SyntaxError("Invalid assignment target")  # Anything else is invalid
        else:
            self._current = checkpoint  # If no '=', restore the pointer to before the expr

        return expr  # Return the expression if it wasn't an assignment

    
    def _class_declaration(self):
        # Check if the next token is an identifier (class name), if not raise error
        if not self._match(TokenType.IDENTIFIER):
            raise SyntaxError("Expected class name")
        class_name = self._previous().lexeme  # Get the class name from the last matched token

        # Expect an opening brace to start the class body
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError("Expected '{' after class name")

        body = []  # List to hold class body statements (like field assignments)
        # Keep parsing statements until we find the closing brace or reach EOF
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            stmt = self._statement()
            if stmt:
                body.append(stmt)  # Add each statement to the body list

        # After parsing body, expect a closing brace
        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError("Expected '}' after class body")

        return Class(class_name, body)  # Return a Class expression node

    def _return_statement(self):
        value = None  # Default return value is None if nothing follows 'return'

        # If we're not immediately at the end of a block, parse the return expression
        if not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            value = self._expression()  # Parse the expression after 'return'

        return Return(value)  # Wrap it in a Return node (even if it's None)

    def _function_declaration(self):
        name_token = self._advance()  # Consume the function name token
        if name_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Expected function name after 'fun'")

        # Check for opening parenthesis after function name
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError("Expected '(' after function name")

        param_names = []  # List of parameter names
        if not self._check(TokenType.RIGHT_PAREN):  # If not empty parameter list
            while True:
                param_token = self._advance()  # Get the next parameter
                if param_token.type != TokenType.IDENTIFIER:
                    raise SyntaxError("Expected parameter name")
                param_names.append(param_token.lexeme)  # Add to param list

                # If no comma follows, break (end of param list)
                if not self._match(TokenType.COMMA):
                    break

        # Expect closing parenthesis after all parameters
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError("Expected ')' after parameters")

        # Expect opening brace to start the function body
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError("Expected '{' before function body")

        body = []  # List to hold statements in function body
        # Keep parsing body statements until closing brace or EOF
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            stmt = self._statement()
            if stmt:
                body.append(stmt)

        # After parsing body, expect a closing brace
        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError("Expected '}' after function body")

        # Return a Function node with name, parameters, and body
        return Function(name_token.lexeme, param_names, body)


    def _if_statement(self):

        # Ensure the next token is a LEFT_PAREN (opening parenthesis after 'if')
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(f"Expected '(' after 'if' at line {self._peek().line}")

        condition = self._expression()  # Parse the condition expression inside parentheses

        # Ensure a RIGHT_PAREN follows the condition
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(f"Expected ')' after condition at line {self._peek().line}")

        # Ensure a LEFT_BRACE is present to open the 'then' block
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError(f"Expected '{{' to start if-block at line {self._peek().line}")

        then_branch = []  # List to hold the statements inside the if-block

        # Keep parsing statements until we hit a closing brace or EOF
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            stmt = self._statement()
            if stmt is not None:
                then_branch.append(stmt)

        # Ensure a RIGHT_BRACE is present to close the if-block
        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError(f"Expected '}}' to close if-block at line {self._peek().line}")

        # --- Check for optional elsif blocks ---
        has_elsif = False  # Track if any elsif branches exist
        condition_pairs = [(condition, then_branch)]  # Initialize the condition-action pair list

        # Parse one or more elsif branches
        while self._match(TokenType.ELSIF):
            has_elsif = True  # Mark that we've entered an elsif block

            # Expect parentheses around the elsif condition
            if not self._match(TokenType.LEFT_PAREN):
                raise SyntaxError("Expected '(' after 'elsif'")
            elsif_condition = self._expression()

            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError("Expected ')' after 'elsif' condition")

            # Expect opening brace for elsif block
            if not self._match(TokenType.LEFT_BRACE):
                raise SyntaxError("Expected '{' to start 'elsif' block")

            elsif_branch = []  # List of statements inside the elsif block

            # Keep reading until we close the elsif block
            while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
                stmt = self._statement()
                if stmt is not None:
                    elsif_branch.append(stmt)

            # Expect closing brace for the elsif block
            if not self._match(TokenType.RIGHT_BRACE):
                raise SyntaxError("Expected '}' to close 'elsif' block")

            # Add the elsif condition and its body to the list
            condition_pairs.append((elsif_condition, elsif_branch))

        # --- Optional else block ---
        else_branch = None  # Default is no else block

        # Check for else
        if self._match(TokenType.ELSE):
            # Expect opening brace for else block
            if not self._match(TokenType.LEFT_BRACE):
                raise SyntaxError(f"Expected '{{' to start else-block at line {self._peek().line}")

            else_branch = []  # List of statements in the else block

            # Parse until closing brace
            while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
                stmt = self._statement()
                if stmt is not None:
                    else_branch.append(stmt)

            # Ensure the else block ends correctly
            if not self._match(TokenType.RIGHT_BRACE):
                raise SyntaxError(f"Expected '}}' to close else-block at line {self._peek().line}")

        # --- Return final result ---
        if has_elsif:
            # If there were any elsif branches, return an IfChain expression
            return IfChain(condition_pairs, else_branch)
        else:
            # Otherwise return a standard If expression
            return If(condition, then_branch, else_branch)

    
    def _while_statement(self):
        # Ensure the while loop starts with a '(' for the condition
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(f"Expected '(' after 'while' at line {self._peek().line}")

        condition = self._expression()  # Parse the boolean condition expression

        # Ensure the condition is properly closed with ')'
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(f"Expected ')' after condition at line {self._peek().line}")

        # Expect the '{' to begin the while-loop body block
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError(f"Expected '{{' to start while-block at line {self._peek().line}")

        body = []  # Collect all statements inside the while loop
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            stmt = self._statement()
            if stmt is not None:
                body.append(stmt)

        # Ensure the loop body ends with a closing '}'
        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError(f"Expected '}}' to close while-block at line {self._peek().line}")

        return While(condition, body)  # Return the While AST node with condition and body


    def _for_loop(self):
        # A for loop must start with a '(' before initializer
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError("Expected '(' after 'for'")

        initializer = None

        # Check for a variable assignment like i = 0
        if self._check(TokenType.IDENTIFIER) and self._check_next(TokenType.EQUAL):
            initializer = self._assignment()  # Parse the initializer
        else:
            raise SyntaxError("Expected initialization (e.g., i = 0)")

        # Expect the first semicolon to terminate the initializer
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError("Expected ';' after initializer")

        condition = self._expression()  # Parse the boolean loop condition

        # Expect the second semicolon after the condition
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError("Expected ';' after condition")

        increment = self._assignment()  # Parse the increment statement

        # Expect closing ')' after initializer;condition;increment
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError("Expected ')' after for loop increment")

        # Expect opening '{' for the for-loop body
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError("Expected '{' to start for-loop block")

        body = []  # Collect all statements inside the loop body
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            stmt = self._statement()
            if stmt:
                body.append(stmt)

        # Expect closing '}' after loop body
        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError("Expected '}' to close for-loop block")

        return For(initializer, condition, increment, body)  # Return the For AST node

    
    #---------------------------------------------------
    # Expression Parsing Functions (Recursive Descent) |
    #---------------------------------------------------

    # This is the starting point of parsing
    # _expression() Parses the full expression
    def _assignment(self):
        # First parse the left-hand side, which could be a variable or a field access
        expr = self._expression()

        # If there's no '=' after it, it's not an assignment
        if not self._match(TokenType.EQUAL):
            return expr  # Just return the original expression (not an assignment)

        # Parse the right-hand side of the assignment
        value = self._expression()

        # Handle variable assignment (x = ...)
        if isinstance(expr, Variable):
            return Assignment(expr.name, value)

        # Handle object field assignment (p.name = ...)
        if isinstance(expr, GetField):
            return SetField(expr.object_expr, expr.field_name, value)

        # If it's not assignable
        raise SyntaxError("Invalid assignment target")

    
    def _expression(self, verbose=True):
        return self._logical_or(verbose)  # Calls _logical_or() which handles boolean or (or) operations

    # Handle or boolean expressions
    def _logical_or(self, verbose=True):
        expression = self._logical_and(verbose)  # Calls _logical_and() to parse the left-hand side

        # if "or" is found
        while self._match(TokenType.OR):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")  # error: true or
            operator = self._previous()  # Store the operator "or"
            right = self._logical_and(verbose)  # Parse the right-hand side
            expression = Binary(expression, operator, right)  # Construct a binary expression
        return expression  # Return the complete or expression

    # The same for the and boolean operator
    def _logical_and(self, verbose=True):
        expression = self._equality(verbose)  # Left-hand side
        while self._match(TokenType.AND):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._equality(verbose)  # right-hand side
            expression = Binary(expression, operator, right)
        return expression

    # Handles == , != operators
    def _equality(self, verbose=True):
        expression = self._comparison(verbose)
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._comparison(verbose)
            expression = Binary(expression, operator, right)
        return expression

    # Handles <, <=, >, >= operators
    def _comparison(self, verbose=True):
        expression = self._term(verbose)
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._term(verbose)
            expression = Binary(expression, operator, right)
        return expression

    # Handles +, - operators
    def _term(self, verbose=True):
        expression = self._factor(verbose)
        while self._match(TokenType.PLUS, TokenType.MINUS):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._factor(verbose)
            expression = Binary(expression, operator, right)
        return expression

    # Handles /, *, % operators
    def _factor(self, verbose=True):
        expression = self._exponent(verbose)
        while self._match(TokenType.DIV, TokenType.TIMES, TokenType.MOD):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._exponent(verbose)
            expression = Binary(expression, operator, right)
        return expression

    # Handles ** operator
    def _exponent(self, verbose=True):
        expression = self._unary(verbose)
        while self._match(TokenType.EXP):
            if self._at_end():  
                raise SyntaxError(f"Missing operand after '{self._previous().lexeme}'")
            operator = self._previous()
            right = self._unary(verbose)
            expression = Binary(expression, operator, right)
        return expression

    # handles unary operations like -2 * 3 or !true
    def _unary(self, verbose=True):
        # If it is '-', parse the right operand
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._unary(verbose)
            return Unary(operator, right)

        # If it is '!', parse the right operand
        if self._match(TokenType.BANG):
            operator = self._previous()
            right = self._unary(verbose)

            # If right is a grouping, evaluate it first
            if isinstance(right, Grouping):
                right = Literal(right.evaluate(self.variables, verbose))  # <- FIXED HERE

            # Ensure '!' is only used with booleans
            if not isinstance(right, Literal) or not isinstance(right.value, bool):
                raise SyntaxError(f"Syntax Error: '!' must be followed by a Boolean, found '{right}'.")

            return Unary(operator, right)

        return self._primary()

    def _primary(self):
        # Match a numeric literal (float or int) and return a Literal node
        if self._match(TokenType.FLOAT):
            if self._check(TokenType.BANG):  # Disallow something like `5!`
                raise SyntaxError(f"Syntax Error: Unexpected token '!' after number.")
            return Literal(self._previous().literal)  # Create a Literal with the matched float value

        # Match a string literal like "hello"
        if self._match(TokenType.STRING):  
            return Literal(self._previous().literal)  # Return as a Literal node

        # Match a boolean literal (true or false)
        if self._match(TokenType.BOOLEAN):  
            return Literal(self._previous().literal)  # Return as a Literal node

        # Match an identifier (could be variable or function name)
        if self._match(TokenType.IDENTIFIER):
            name_token = self._previous()  # Save the identifier token
            expr = Variable(name_token)  # Initially treat it as a variable

            # Handle chained expressions like function calls, indexing, field access
            while True:
                # If it's a function call like name(...), parse arguments
                if self._match(TokenType.LEFT_PAREN):
                    arguments = []
                    if not self._check(TokenType.RIGHT_PAREN):  # Allow multiple args
                        while True:
                            arguments.append(self._expression())  # Parse each argument
                            if not self._match(TokenType.COMMA):
                                break
                    if not self._match(TokenType.RIGHT_PAREN):
                        raise SyntaxError("Expected ')' after function arguments")

                    # Special handling for built-in float() and str()
                    if isinstance(expr, Variable) and expr.name.lexeme == "float":
                        if len(arguments) != 1:
                            raise SyntaxError("float() expects exactly 1 argument")
                        return ToFloat(arguments[0])
                    
                    if isinstance(expr, Variable) and expr.name.lexeme == "str":
                        if len(arguments) != 1:
                            raise SyntaxError("str() expects exactly 1 argument")
                        return ToString(arguments[0])

                    # If it's a regular function call, wrap it
                    expr = FunctionCall(expr, arguments)

                # Handle indexing like arr[1]
                elif self._match(TokenType.LEFT_BRACKET):
                    index_expr = self._expression()
                    if not self._match(TokenType.RIGHT_BRACKET):
                        raise SyntaxError("Expected ']' after index")
                    expr = IndexAccess(expr, index_expr)

                # Handle field access like obj.name
                elif self._match(TokenType.DOT):
                    field = self._advance()
                    if field.type != TokenType.IDENTIFIER:
                        raise SyntaxError("Expected property name after '.'")
                    expr = GetField(expr, field)

                else:
                    break  # No more chaining; stop here

            return expr  # Return the fully built expression

        # Match the ask keyword, e.g., ask "What is your name?"
        if self._match(TokenType.ASK):
            prompt_expr = self._expression()
            return Ask(prompt_expr)  # Return Ask expression node

        # Match parenthesized expressions like (x + y)
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError(
                    f"Syntax Error: Missing closing parenthesis ')' at line {self._peek().line}, column {self._peek().col}."
                )
            return Grouping(expression)

        # Match list literals like [1, 2, 3]
        if self._match(TokenType.LEFT_BRACKET):
            elements = []
            if not self._check(TokenType.RIGHT_BRACKET):  # Allow empty list
                while True:
                    elements.append(self._expression())  # Parse each element
                    if not self._match(TokenType.COMMA):
                        break
            if not self._match(TokenType.RIGHT_BRACKET):
                raise SyntaxError("Expected ']' after list literal")
            return ListLiteral(elements)

        # If no valid primary token matched, raise syntax error
        raise SyntaxError(
            f"Unexpected token: '{self._peek().lexeme}' at line {self._peek().line}, column {self._peek().col}."
        )


