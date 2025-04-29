"""
Lexical Analyzer (Scanner) for the Mini Compiler.
This module handles tokenization of the input source code.
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional

class TokenType(Enum):
    # Keywords
    PROGRAM = auto()
    VAR = auto()
    INTEGER = auto()
    FLOAT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINT = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    
    # Comparisons
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    
    # Others
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    EOF = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class LexicalError(Exception):
    """Exception raised for lexical analysis errors."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.line = line
        self.column = column

class Lexer:
    """
    Lexical Analyzer that converts source code into tokens.
    """
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source_code[0] if source_code else None
        
        # Define token patterns
        self.keywords = {
            'brainrot': TokenType.PROGRAM,
            'tongtongsahur': TokenType.VAR,
            'bombardino': TokenType.INTEGER,
            'crocodilo': TokenType.FLOAT,
            'chimpanzini': TokenType.IF,
            'bananini': TokenType.ELSE,
            'patapim': TokenType.WHILE,
            'drip': TokenType.PRINT,
        }
        
        self.operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.ASSIGN,
            '==': TokenType.EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON,
            '<=': TokenType.LESS_THAN_OR_EQUAL,
            '>=': TokenType.GREATER_THAN_OR_EQUAL,
        }

    def advance(self):
        """Move to the next character in the source code."""
        self.position += 1
        self.column += 1
        
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            self.current_char = self.source_code[self.position]

    def peek(self) -> Optional[str]:
        """Look at the next character without consuming it."""
        peek_pos = self.position + 1
        if peek_pos >= len(self.source_code):
            return None
        return self.source_code[peek_pos]

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """Skip single-line comments."""
        # Skip the '#' character
        self.advance()
        
        # Continue until end of line or end of file
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        result = ''
        column_start = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if it's a keyword
        token_type = self.keywords.get(result.lower(), TokenType.IDENTIFIER)
        token = Token(token_type, result, self.line, column_start)
        print(f"Found identifier/keyword: {token}")
        return token

    def read_number(self) -> Token:
        """Read a number (integer or float)."""
        result = ''
        column_start = self.column
        is_float = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    raise LexicalError(
                        "Invalid number format: multiple decimal points",
                        self.line,
                        self.column
                    )
                is_float = True
            result += self.current_char
            self.advance()

        token = Token(
            TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER_LITERAL,
            result,
            self.line,
            column_start
        )
        print(f"Found number: {token}")
        return token

    def get_next_token(self) -> Token:
        """
        Get the next token from the source code.
        Returns Token object containing the token type and value.
        """
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Skip comments
            if self.current_char == '#':
                print(f"Found comment at line {self.line}")
                self.skip_comment()
                continue

            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()

            # Numbers
            if self.current_char.isdigit():
                return self.read_number()

            # Multi-character operators
            next_char = self.peek() or ''
            two_char = self.current_char + next_char
            if two_char in self.operators:
                operator = two_char
                token = Token(self.operators[operator], operator, self.line, self.column)
                self.advance()
                self.advance()
                print(f"Found operator: {token}")
                return token

            # Single-character operators
            if self.current_char in self.operators:
                token = Token(self.operators[self.current_char], self.current_char, self.line, self.column)
                self.advance()
                print(f"Found operator: {token}")
                return token

            # Invalid character
            raise LexicalError(
                f"Invalid character '{self.current_char}'",
                self.line,
                self.column
            )

        # End of file
        token = Token(TokenType.EOF, '', self.line, self.column)
        print(f"Found EOF: {token}")
        return token

    def tokenize(self) -> List[Token]:
        """
        Convert the entire source code into a list of tokens.
        Returns a list of Token objects.
        """
        print("\nStarting tokenization...")
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        print(f"\nTokenization complete. Found {len(tokens)} tokens.")
        return tokens 