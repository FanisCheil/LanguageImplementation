from Token import Token, TokenType
from typing import List

class Scanner:
    #It accepts a string, source, which will be the input to tokenize
    def __init__(self, source: str) -> None:
        self.source: str = source # Sotre the input string in self.source
        self.tokens: list[Token] = [] #Initialize an empty list to store tokens
        self._line: int = 1 #Track the current line
        self._col: int = 1 #Track the current column
        self._cur_char_index: int = 0 #Here we store the index of the current character in self.source...This will be incremented each time the advance() method is called

        self._cur_char: str = "" # Hold the current character we process. This is being update when advance() is called as well
    
    #Move to and return the next character in the input
    def advance(self) -> str:
        #Check is we reached the end of the input and if so return an empty string
        if self._cur_char_index == len(self.source):
            return ""
        #If not  
        
        self._cur_char = self.source[self._cur_char_index] #Retrive the next character from self.source and store it
        
        self._cur_char_index += 1 #Move the character index so the next call to advance gets the next character

        self._col += 1#Update the column count to track where we are in the input

        return self._cur_char # Return the newly advanced character

    #This function looks at the nect character without advancing
    def peek(self) -> str:
        if self._cur_char_index == len(self.source):
            return ""  
        #Return the next character without advancing the index
        return self.source[self._cur_char_index]
    
    #Detect and process numbers both floats and decimals
    def _scan_float(self) -> None:
        fl = self._cur_char #Store the curnent character

        #Loop through the input as long as:
        # - The next char is a digit
        # - Or the next char is a decimal point (.)
        while self.peek().isdigit() or self.peek() == ".":
            fl += self.advance() #Append each valid character using advance()

        #Create a FLOAT token and add it to self.tokens
        #Also converts the fl to a float    
        self.tokens.append(Token(TokenType.FLOAT, fl, float(fl), self._line, self._col))

    #Scans strings(Text inside "")
    def _scan_string(self) -> None:
        string_value = "" #Srore the characters inside the quotes

        #Add characters to string_value until we reach
        # - A closing " 
        # - the end of input
        while self.peek() != '"' and self.peek() != "":
            string_value += self.advance()

        #iF the input ends without a closing ". raise and error
        if self.peek() == "":
            raise SyntaxError("Unterminated string literal")
        
        #Consume the closing "
        self.advance()

        #Create a STRING token and add it to self.tokens
        self.tokens.append(Token(TokenType.STRING, string_value, string_value, self._line, self._col))
    
    #Hanldes newlines
    def _scan_newline(self) -> None:
        self.tokens.append(Token(TokenType.NEWLN, "\\n", None, self._line, self._col)) #Add a NEWLN token to represent the new line
        self._line += 1 #increment the line coutner
        self._col = 1 #Reset the column counter to 1
    
    # The main function. Our "Tokenizer". This fucntion processes the entire input and splits it into tokens
    def scan_tokens(self) -> List[Token]:

        #Define the keywords true, false, and, or, print
        keywords = {
            "true": TokenType.BOOLEAN,
            "false": TokenType.BOOLEAN,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "ask": TokenType.ASK,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "elsif": TokenType.ELSIF,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "return": TokenType.RETURN,
            "class": TokenType.CLASS
        }
        
        #Loop through every character in the input
        while (c := self.advance()) != "": 
            if c.isspace():  #Skip spaces
                continue
            elif c == "+":  #Detect and store + as a PLUS token
                self.tokens.append(Token(TokenType.PLUS, c, None, self._line, self._col))
            elif c == "-":  #Detect and store - as a MINUS token
                self.tokens.append(Token(TokenType.MINUS, c, None, self._line, self._col))
            elif c == "*" and self.peek() == "*":  
                self.advance()  #Consume the 2nd *
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
            elif c == "{":
                self.tokens.append(Token(TokenType.LEFT_BRACE, c, None, self._line, self._col))
            elif c == "}":
                self.tokens.append(Token(TokenType.RIGHT_BRACE, c, None, self._line, self._col))
            elif c == "[":
                self.tokens.append(Token(TokenType.LEFT_BRACKET, c, None, self._line, self._col))
            elif c == "]":
                self.tokens.append(Token(TokenType.RIGHT_BRACKET, c, None, self._line, self._col))
            elif c == ",":
                self.tokens.append(Token(TokenType.COMMA, c, None, self._line, self._col))
            elif c == ";":
                self.tokens.append(Token(TokenType.SEMICOLON, c, None, self._line, self._col))
            elif c == ".":
                self.tokens.append(Token(TokenType.DOT, c, None, self._line, self._col))
            elif c == "!":
                if self.peek() == "=":
                    self.advance()
                    self.tokens.append(Token(TokenType.BANG_EQUAL, "!=", None, self._line, self._col))
                else:
                    self.tokens.append(Token(TokenType.BANG, c, None, self._line, self._col))
            elif c == "=":
                if self.peek() == "=":
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL_EQUAL, "==", None, self._line, self._col))
                else:
                    self.tokens.append(Token(TokenType.EQUAL, c, None, self._line, self._col))
            elif c == "<":
                if self.peek() == "=":
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", None, self._line, self._col))
                else:
                    self.tokens.append(Token(TokenType.LESS, c, None, self._line, self._col))
            elif c == ">":
                if self.peek() == "=":
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", None, self._line, self._col))
                else:
                    self.tokens.append(Token(TokenType.GREATER, c, None, self._line, self._col))
            elif c.isdigit():  
                self._scan_float()
            elif c == '"':  
                self._scan_string()
            elif c.isalpha() or c == "_":  #handle keywords and identifiers
                lexeme = c
                while self.peek().isalnum() or self.peek() == "_":
                    lexeme += self.advance()
                token_type = keywords.get(lexeme, None)
                if token_type:
                    self.tokens.append(Token(token_type, lexeme, lexeme == "true", self._line, self._col))
                else:
                    # Treat it as a user-defined identifier (e.g. variable name)
                    self.tokens.append(Token(TokenType.IDENTIFIER, lexeme, None, self._line, self._col))
            elif c == "\n":
                self._scan_newline()
            else:
                raise SyntaxError(f"Unexpected token: '{c}' at line {self._line}, column {self._col}")
        
        #Mark the end of the input and return all tokens
        self.tokens.append(Token(TokenType.EOF, "", None, self._line, self._col))
        return self.tokens
