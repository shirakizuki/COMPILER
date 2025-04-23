"""
Syntax Analyzer (Parser) for the Mini Compiler.
This module implements an LL(1) parser to create an Abstract Syntax Tree (AST).
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from .lexer import Token, TokenType, LexicalError

class ParseError(Exception):
    """Exception raised for parsing errors."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.line = line
        self.column = column

# AST Node classes
@dataclass
class Node:
    """Base class for all AST nodes."""
    pass

@dataclass
class Program(Node):
    """Root node of the program."""
    declarations: List['VarDeclaration']
    statements: List['Statement']

@dataclass
class VarDeclaration(Node):
    """Variable declaration node."""
    name: str
    type: str
    line: int
    column: int

@dataclass
class Statement(Node):
    """Base class for all statement nodes."""
    pass

@dataclass
class AssignmentStmt(Statement):
    """Assignment statement node."""
    variable: str
    expression: 'Expression'
    line: int
    column: int

@dataclass
class IfStmt(Statement):
    """If statement node."""
    condition: 'Expression'
    then_block: List[Statement]
    elif_blocks: List[tuple['Expression', List[Statement]]]  # List of (condition, statements) pairs
    else_block: Optional[List[Statement]]
    line: int
    column: int

@dataclass
class WhileStmt(Statement):
    """While loop statement node."""
    condition: 'Expression'
    body: List[Statement]
    line: int
    column: int

@dataclass
class Expression(Node):
    """Base class for all expression nodes."""
    pass

@dataclass
class PrintStmt(Statement):
    """Print statement node."""
    expression: Expression
    line: int
    column: int

@dataclass
class BinaryOp(Expression):
    """Binary operation node."""
    left: Expression
    operator: Token
    right: Expression
    line: int
    column: int

@dataclass
class UnaryOp(Expression):
    """Unary operation node."""
    operator: Token
    operand: Expression
    line: int
    column: int

@dataclass
class Literal(Expression):
    """Literal value node."""
    value: Union[int, float]
    line: int
    column: int

@dataclass
class Identifier(Expression):
    """Variable reference node."""
    name: str
    line: int
    column: int

class Parser:
    """
    LL(1) Parser that generates an Abstract Syntax Tree.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.debug_indent = 0

    def debug_print(self, message: str):
        """Print debug message with indentation."""
        print("  " * self.debug_indent + message)

    def match(self, expected_type: TokenType) -> Token:
        """Match current token with expected type and advance."""
        if self.current >= len(self.tokens):
            raise ParseError(f"Unexpected end of input, expected {expected_type}", -1, -1)
        
        current_token = self.tokens[self.current]
        if current_token.type == expected_type:
            self.debug_print(f"Matched {current_token}")
            self.current += 1
            return current_token
        raise ParseError(
            f"Expected {expected_type} but got {current_token.type}",
            current_token.line,
            current_token.column
        )

    def peek(self) -> Token:
        """Look at current token without consuming it."""
        if self.current >= len(self.tokens):
            return Token(TokenType.EOF, '', -1, -1)
        return self.tokens[self.current]

    def parse_program(self) -> Program:
        """Parse the complete program."""
        self.debug_print("Parsing program")
        self.debug_indent += 1
        
        declarations = []
        statements = []
        
        # Parse variable declarations
        while self.peek().type == TokenType.VAR:
            self.debug_print("Found variable declaration")
            declarations.append(self.parse_declaration())
            
        # Parse statements
        while self.peek().type != TokenType.EOF:
            self.debug_print(f"Found statement starting with {self.peek()}")
            statements.append(self.parse_statement())
            
        self.debug_indent -= 1
        return Program(declarations, statements)

    def parse_declaration(self) -> VarDeclaration:
        """Parse variable declaration."""
        self.debug_print("Parsing declaration")
        self.debug_indent += 1
        
        self.match(TokenType.VAR)
        name_token = self.match(TokenType.IDENTIFIER)
        self.match(TokenType.ASSIGN)
        type_token = self.match(TokenType.INTEGER) if self.peek().type == TokenType.INTEGER else self.match(TokenType.FLOAT)
        self.match(TokenType.SEMICOLON)
        
        self.debug_indent -= 1
        return VarDeclaration(
            name_token.value,
            type_token.value,
            name_token.line,
            name_token.column
        )

    def parse_statement(self) -> Statement:
        """Parse a statement."""
        self.debug_print("Parsing statement")
        self.debug_indent += 1
        
        token = self.peek()
        result = None
        
        if token.type == TokenType.IDENTIFIER:
            result = self.parse_assignment()
        elif token.type == TokenType.IF:
            result = self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            result = self.parse_while_statement()
        elif token.type == TokenType.PRINT:
            result = self.parse_print_statement()
        else:
            raise ParseError(
                f"Unexpected token {token.type}",
                token.line,
                token.column
            )
            
        self.debug_indent -= 1
        return result

    def parse_assignment(self) -> AssignmentStmt:
        """Parse assignment statement."""
        self.debug_print("Parsing assignment")
        self.debug_indent += 1
        
        identifier = self.match(TokenType.IDENTIFIER)
        self.match(TokenType.ASSIGN)
        expression = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        
        self.debug_indent -= 1
        return AssignmentStmt(
            identifier.value,
            expression,
            identifier.line,
            identifier.column
        )

    def parse_if_statement(self) -> IfStmt:
        """Parse if statement."""
        self.debug_print("Parsing if statement")
        self.debug_indent += 1
        
        if_token = self.match(TokenType.IF)
        self.match(TokenType.LPAREN)
        condition = self.parse_expression()
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        
        then_block = []
        while self.peek().type != TokenType.RBRACE:
            then_block.append(self.parse_statement())
        self.match(TokenType.RBRACE)
        
        elif_blocks = []
        else_block = None
        
        # Parse else if blocks
        while self.peek().type == TokenType.IF:
            self.match(TokenType.IF)  # Consume 'if'
            self.match(TokenType.LPAREN)
            elif_condition = self.parse_expression()
            self.match(TokenType.RPAREN)
            self.match(TokenType.LBRACE)
            
            elif_statements = []
            while self.peek().type != TokenType.RBRACE:
                elif_statements.append(self.parse_statement())
            self.match(TokenType.RBRACE)
            
            elif_blocks.append((elif_condition, elif_statements))
        
        # Parse else block if present
        if self.peek().type == TokenType.ELSE:
            self.match(TokenType.ELSE)
            self.match(TokenType.LBRACE)
            
            else_block = []
            while self.peek().type != TokenType.RBRACE:
                else_block.append(self.parse_statement())
            self.match(TokenType.RBRACE)
        
        self.debug_indent -= 1
        return IfStmt(condition, then_block, elif_blocks, else_block, if_token.line, if_token.column)

    def parse_while_statement(self) -> WhileStmt:
        """Parse while statement."""
        self.debug_print("Parsing while statement")
        self.debug_indent += 1
        
        token = self.match(TokenType.WHILE)
        self.match(TokenType.LPAREN)
        condition = self.parse_expression()
        self.match(TokenType.RPAREN)
        
        self.match(TokenType.LBRACE)
        body = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.match(TokenType.RBRACE)
        
        self.debug_indent -= 1
        return WhileStmt(condition, body, token.line, token.column)

    def parse_print_statement(self) -> PrintStmt:
        """Parse print statement."""
        self.debug_print("Parsing print statement")
        self.debug_indent += 1
        
        token = self.match(TokenType.PRINT)
        self.match(TokenType.LPAREN)
        expression = self.parse_expression()
        self.match(TokenType.RPAREN)
        self.match(TokenType.SEMICOLON)
        
        self.debug_indent -= 1
        return PrintStmt(expression, token.line, token.column)

    def parse_expression(self) -> Expression:
        """Parse expression."""
        self.debug_print("Parsing expression")
        self.debug_indent += 1
        result = self.parse_comparison()
        self.debug_indent -= 1
        return result

    def parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        self.debug_print("Parsing comparison")
        self.debug_indent += 1
        
        expr = self.parse_additive()
        
        while self.peek().type in [TokenType.EQUALS, TokenType.NOT_EQUALS, 
                                 TokenType.LESS_THAN, TokenType.GREATER_THAN]:
            operator = self.peek()
            self.debug_print(f"Found comparison operator: {operator}")
            self.current += 1
            right = self.parse_additive()
            expr = BinaryOp(expr, operator, right, operator.line, operator.column)
            
        self.debug_indent -= 1
        return expr

    def parse_additive(self) -> Expression:
        """Parse additive expression."""
        self.debug_print("Parsing additive")
        self.debug_indent += 1
        
        expr = self.parse_multiplicative()
        
        while self.peek().type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.peek()
            self.debug_print(f"Found additive operator: {operator}")
            self.current += 1
            right = self.parse_multiplicative()
            expr = BinaryOp(expr, operator, right, operator.line, operator.column)
            
        self.debug_indent -= 1
        return expr

    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expression."""
        self.debug_print("Parsing multiplicative")
        self.debug_indent += 1
        
        expr = self.parse_primary()
        
        while self.peek().type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            operator = self.peek()
            self.debug_print(f"Found multiplicative operator: {operator}")
            self.current += 1
            right = self.parse_primary()
            expr = BinaryOp(expr, operator, right, operator.line, operator.column)
            
        self.debug_indent -= 1
        return expr

    def parse_primary(self) -> Expression:
        """Parse primary expression."""
        self.debug_print("Parsing primary")
        self.debug_indent += 1
        
        token = self.peek()
        result = None
        
        if token.type in [TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL]:
            self.debug_print(f"Found literal: {token}")
            self.current += 1
            value = int(token.value) if token.type == TokenType.INTEGER_LITERAL else float(token.value)
            result = Literal(value, token.line, token.column)
            
        elif token.type == TokenType.IDENTIFIER:
            self.debug_print(f"Found identifier: {token}")
            self.current += 1
            result = Identifier(token.value, token.line, token.column)
            
        elif token.type == TokenType.LPAREN:
            self.debug_print("Found parenthesized expression")
            self.current += 1
            result = self.parse_expression()
            self.match(TokenType.RPAREN)
            
        elif token.type in [TokenType.PLUS, TokenType.MINUS]:
            self.debug_print(f"Found unary operator: {token}")
            self.current += 1
            operand = self.parse_primary()
            result = UnaryOp(token, operand, token.line, token.column)
            
        else:
            raise ParseError(
                f"Unexpected token {token.type}",
                token.line,
                token.column
            )
            
        self.debug_indent -= 1
        return result

    def parse(self) -> Program:
        """Parse the complete program and return AST."""
        print("\nStarting parsing...")
        ast = self.parse_program()
        print("\nParsing complete!")
        return ast 