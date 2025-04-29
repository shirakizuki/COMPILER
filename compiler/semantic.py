"""
Semantic Analyzer for the Mini Compiler.
This module performs type checking and scope validation.
"""

from typing import Dict, Set, Optional
from .parser import (
    Node, Program, VarDeclaration, Statement, AssignmentStmt,
    IfStmt, WhileStmt, Expression, BinaryOp, UnaryOp, Literal,
    Identifier, PrintStmt
)
from .lexer import TokenType

class SemanticError(Exception):
    """Exception raised for semantic errors."""
    pass

class Symbol:
    """Symbol table entry."""
    def __init__(self, name: str, type_: str, line: int, column: int):
        self.name = name
        self.type = type_
        self.line = line
        self.column = column

class SymbolTable:
    """Symbol table for tracking variable declarations and types."""
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        
    def declare(self, name: str, type_: str, line: int, column: int) -> None:
        """Declare a new variable."""
        if name in self.symbols:
            symbol = self.symbols[name]
            raise SemanticError(
                f"Variable '{name}' already declared at line {symbol.line}, "
                f"column {symbol.column}"
            )
        self.symbols[name] = Symbol(name, type_, line, column)
        
    def lookup(self, name: str, line: int, column: int) -> Symbol:
        """Look up a variable in the symbol table."""
        if name not in self.symbols:
            raise SemanticError(
                f"Undefined variable '{name}' at line {line}, column {column}"
            )
        return self.symbols[name]

class SemanticAnalyzer:
    """
    Semantic analyzer that performs type checking and scope validation.
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, ast: Program) -> None:
        """Analyze the complete program."""
        # Process all declarations first
        for decl in ast.declarations:
            self.visit_declaration(decl)
            
        # Then analyze all statements
        for stmt in ast.statements:
            self.visit_statement(stmt)

    def visit_declaration(self, node: VarDeclaration) -> None:
        """Process variable declaration."""
        self.symbol_table.declare(node.name, node.type, node.line, node.column)

    def visit_statement(self, node: Statement) -> None:
        """Process a statement node."""
        if isinstance(node, AssignmentStmt):
            self.visit_assignment(node)
        elif isinstance(node, IfStmt):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStmt):
            self.visit_while_statement(node)
        elif isinstance(node, PrintStmt):
            self.visit_print_statement(node)
        else:
            raise SemanticError(f"Unknown statement type: {type(node)}")

    def visit_assignment(self, node: AssignmentStmt) -> None:
        """Process assignment statement."""
        # Check variable exists and get its type
        symbol = self.symbol_table.lookup(node.variable, node.line, node.column)
        
        # Check expression type matches variable type
        expr_type = self.visit_expression(node.expression)
        if symbol.type != expr_type:
            raise SemanticError(
                f"Type mismatch in assignment at line {node.line}, column {node.column}. "
                f"Expected {symbol.type}, got {expr_type}"
            )

    def visit_if_statement(self, node: IfStmt) -> None:
        """Process if statement."""
        # Check condition is boolean
        condition_type = self.visit_expression(node.condition)
        if condition_type != "boolean":
            raise SemanticError(
                f"Condition must be boolean at line {node.line}, column {node.column}"
            )
            
        # Check then block
        for stmt in node.then_block:
            self.visit_statement(stmt)
            
        # Check else block if it exists
        if node.else_block:
            for stmt in node.else_block:
                self.visit_statement(stmt)

    def visit_while_statement(self, node: WhileStmt) -> None:
        """Process while statement."""
        # Check condition is boolean
        condition_type = self.visit_expression(node.condition)
        if condition_type != "boolean":
            raise SemanticError(
                f"Condition must be boolean at line {node.line}, column {node.column}"
            )
            
        # Check body
        for stmt in node.body:
            self.visit_statement(stmt)

    def visit_print_statement(self, node: PrintStmt) -> None:
        """Process print statement."""
        # Just verify that the expression is valid
        self.visit_expression(node.expression)

    def visit_expression(self, node: Expression) -> str:
        """Process an expression node and return its type."""
        if isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Literal):
            return self.visit_literal(node)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        else:
            raise SemanticError(f"Unknown expression type: {type(node)}")

    def visit_binary_op(self, node: BinaryOp) -> str:
        """Process binary operation and return result type."""
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        
        # Type checking rules for operators
        if node.operator.type in [TokenType.PLUS, TokenType.MINUS, 
                                TokenType.MULTIPLY, TokenType.DIVIDE]:
            if left_type != right_type:
                raise SemanticError(
                    f"Type mismatch in binary operation at line {node.line}, "
                    f"column {node.column}. Cannot operate on {left_type} and {right_type}"
                )
            return left_type
            
        elif node.operator.type in [TokenType.EQUALS, TokenType.NOT_EQUALS,
                                  TokenType.LESS_THAN, TokenType.GREATER_THAN,
                                  TokenType.LESS_THAN_OR_EQUAL, TokenType.GREATER_THAN_OR_EQUAL]:
            if left_type != right_type:
                raise SemanticError(
                    f"Type mismatch in comparison at line {node.line}, "
                    f"column {node.column}. Cannot compare {left_type} and {right_type}"
                )
            return "boolean"
            
        else:
            raise SemanticError(
                f"Unknown operator {node.operator.type} at line {node.line}, "
                f"column {node.column}"
            )

    def visit_unary_op(self, node: UnaryOp) -> str:
        """Process unary operation and return result type."""
        operand_type = self.visit_expression(node.operand)
        
        if node.operator.type in [TokenType.PLUS, TokenType.MINUS]:
            if operand_type not in ["bombardino", "crocodilo"]:
                raise SemanticError(
                    f"Invalid type for unary operator at line {node.line}, "
                    f"column {node.column}. Expected number, got {operand_type}"
                )
            return operand_type
            
        else:
            raise SemanticError(
                f"Unknown unary operator {node.operator.type} at line {node.line}, "
                f"column {node.column}"
            )

    def visit_literal(self, node: Literal) -> str:
        """Process literal value and return its type."""
        if isinstance(node.value, int):
            return "bombardino"
        elif isinstance(node.value, float):
            return "crocodilo"
        else:
            raise SemanticError(f"Unknown literal type: {type(node.value)}")

    def visit_identifier(self, node: Identifier) -> str:
        """Process identifier and return its type."""
        symbol = self.symbol_table.lookup(node.name, node.line, node.column)
        return symbol.type 