"""
Intermediate Code Generator for the Mini Compiler.
This module generates Three-Address Code (TAC) from the AST.
"""

from dataclasses import dataclass
from typing import List, Union, Dict
from .parser import (
    Node, Program, VarDeclaration, Statement, AssignmentStmt,
    IfStmt, WhileStmt, Expression, BinaryOp, UnaryOp, Literal,
    Identifier, PrintStmt
)

@dataclass
class TACInstruction:
    """Base class for TAC instructions."""
    pass

@dataclass
class Print(TACInstruction):
    """Print instruction: print value"""
    value: str

@dataclass
class Assignment(TACInstruction):
    """Assignment instruction: target := source"""
    target: str
    source: str

@dataclass
class BinaryOperation(TACInstruction):
    """Binary operation: target := left op right"""
    target: str
    left: str
    operator: str
    right: str

@dataclass
class UnaryOperation(TACInstruction):
    """Unary operation: target := op operand"""
    target: str
    operator: str
    operand: str

@dataclass
class Label(TACInstruction):
    """Label instruction for jumps"""
    name: str

@dataclass
class Jump(TACInstruction):
    """Unconditional jump to label"""
    target: str

@dataclass
class ConditionalJump(TACInstruction):
    """Conditional jump: if condition goto target"""
    condition: str
    target: str

class IntermediateCodeGenerator:
    """
    Generates Three-Address Code (TAC) from AST.
    """
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.variables: Dict[str, str] = {}  # Maps variable names to their types

    def generate(self, ast: Program) -> List[TACInstruction]:
        """Generate TAC for the complete program."""
        # Process declarations
        for decl in ast.declarations:
            self.visit_declaration(decl)
            
        # Process statements
        for stmt in ast.statements:
            self.visit_statement(stmt)
            
        return self.instructions

    def new_temp(self) -> str:
        """Generate a new temporary variable name."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self) -> str:
        """Generate a new label name."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def visit_declaration(self, node: VarDeclaration) -> None:
        """Process variable declaration."""
        self.variables[node.name] = node.type

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

    def visit_assignment(self, node: AssignmentStmt) -> None:
        """Process assignment statement."""
        expr_result = self.visit_expression(node.expression)
        self.instructions.append(Assignment(node.variable, expr_result))

    def visit_if_statement(self, node: IfStmt) -> None:
        """Process if statement."""
        condition_result = self.visit_expression(node.condition)
        
        else_label = self.new_label()
        end_label = self.new_label()
        
        # Jump to else block if condition is false
        self.instructions.append(ConditionalJump(f"not {condition_result}", else_label))
        
        # Then block
        for stmt in node.then_block:
            self.visit_statement(stmt)
        self.instructions.append(Jump(end_label))
        
        # Else if blocks
        for elif_condition, elif_statements in node.elif_blocks:
            self.instructions.append(Label(else_label))
            else_label = self.new_label()  # New label for next else/elif
            
            # Evaluate elif condition
            elif_result = self.visit_expression(elif_condition)
            self.instructions.append(ConditionalJump(f"not {elif_result}", else_label))
            
            # Execute elif block
            for stmt in elif_statements:
                self.visit_statement(stmt)
            self.instructions.append(Jump(end_label))
        
        # Else block
        self.instructions.append(Label(else_label))
        if node.else_block:
            for stmt in node.else_block:
                self.visit_statement(stmt)
                
        self.instructions.append(Label(end_label))

    def visit_while_statement(self, node: WhileStmt) -> None:
        """Process while statement."""
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Start of loop
        self.instructions.append(Label(start_label))
        
        # Condition
        condition_result = self.visit_expression(node.condition)
        self.instructions.append(ConditionalJump(f"not {condition_result}", end_label))
        
        # Loop body
        for stmt in node.body:
            self.visit_statement(stmt)
        
        # Jump back to condition
        self.instructions.append(Jump(start_label))
        
        # End of loop
        self.instructions.append(Label(end_label))

    def visit_print_statement(self, node: PrintStmt) -> None:
        """Process print statement."""
        value = self.visit_expression(node.expression)
        self.instructions.append(Print(value))

    def visit_expression(self, node: Expression) -> str:
        """Process an expression node and return the result variable."""
        if isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Literal):
            return self.visit_literal(node)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        else:
            raise ValueError(f"Unknown expression type: {type(node)}")

    def visit_binary_op(self, node: BinaryOp) -> str:
        """Process binary operation and return result variable."""
        left_result = self.visit_expression(node.left)
        right_result = self.visit_expression(node.right)
        
        result = self.new_temp()
        self.instructions.append(
            BinaryOperation(result, left_result, node.operator.value, right_result)
        )
        return result

    def visit_unary_op(self, node: UnaryOp) -> str:
        """Process unary operation and return result variable."""
        operand_result = self.visit_expression(node.operand)
        
        result = self.new_temp()
        self.instructions.append(
            UnaryOperation(result, node.operator.value, operand_result)
        )
        return result

    def visit_literal(self, node: Literal) -> str:
        """Process literal value and return its string representation."""
        return str(node.value)

    def visit_identifier(self, node: Identifier) -> str:
        """Process identifier and return its name."""
        return node.name

    def optimize(self) -> None:
        """
        Perform basic optimizations on the generated code.
        Currently implements:
        - Constant folding
        - Dead code elimination
        """
        # Constant folding
        self._constant_folding()
        
        # Dead code elimination
        self._dead_code_elimination()

    def _constant_folding(self) -> None:
        """Perform constant folding optimization."""
        i = 0
        while i < len(self.instructions):
            inst = self.instructions[i]
            
            if isinstance(inst, BinaryOperation):
                try:
                    # Try to evaluate constant expressions
                    left = float(inst.left) if '.' in inst.left else int(inst.left)
                    right = float(inst.right) if '.' in inst.right else int(inst.right)
                    
                    result = None
                    if inst.operator == '+':
                        result = left + right
                    elif inst.operator == '-':
                        result = left - right
                    elif inst.operator == '*':
                        result = left * right
                    elif inst.operator == '/':
                        if right != 0:  # Avoid division by zero
                            result = left / right
                            
                    if result is not None:
                        # Replace the binary operation with a simple assignment
                        self.instructions[i] = Assignment(inst.target, str(result))
                except (ValueError, ZeroDivisionError):
                    pass
                    
            i += 1

    def _dead_code_elimination(self) -> None:
        """Perform dead code elimination optimization."""
        # Find all variables that are used
        used_vars = set()
        for inst in self.instructions:
            if isinstance(inst, Assignment):
                if inst.target.startswith('t'):  # Only consider temporaries
                    continue
                used_vars.add(inst.target)
            elif isinstance(inst, (BinaryOperation, UnaryOperation)):
                if not inst.target.startswith('t'):
                    used_vars.add(inst.target)
                    
        # Remove assignments to unused temporary variables
        self.instructions = [
            inst for inst in self.instructions
            if not (isinstance(inst, (Assignment, BinaryOperation, UnaryOperation)) and
                   inst.target.startswith('t') and
                   inst.target not in used_vars)
        ] 