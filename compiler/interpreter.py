# Interpreter for the Mini Compiler.
# This module executes the generated Three-Address Code (TAC).

from typing import Dict, List
from .intermediate import TACInstruction, Assignment, BinaryOperation, UnaryOperation, Print, Jump, ConditionalJump, Label

class Interpreter:
    # Interpreter that executes Three-Address Code (TAC).
    
    def __init__(self):
        self.variables: Dict[str, float] = {}
        self.temporaries: Dict[str, float] = {}
        self.labels: Dict[str, int] = {}
        self.current_instruction = 0
        
    # Execute the intermediate code.
    def execute(self, instructions: List[TACInstruction]) -> None:
        # First pass: collect label positions
        for i, inst in enumerate(instructions):
            if isinstance(inst, Label):
                self.labels[inst.name] = i
        
        # Second pass: execute instructions
        while self.current_instruction < len(instructions):
            inst = instructions[self.current_instruction]
            self._execute_instruction(inst)
            self.current_instruction += 1
            
    # Execute a single instruction.
    def _execute_instruction(self, inst: TACInstruction) -> None:
        if isinstance(inst, Assignment):
            value = self._get_value(inst.source)
            self._set_value(inst.target, value)
            
        elif isinstance(inst, BinaryOperation):
            left = self._get_value(inst.left)
            right = self._get_value(inst.right)
            result = self._apply_operator(left, inst.operator, right)
            self._set_value(inst.target, result)
            
        elif isinstance(inst, UnaryOperation):
            operand = self._get_value(inst.operand)
            result = self._apply_unary_operator(inst.operator, operand)
            self._set_value(inst.target, result)
            
        elif isinstance(inst, Print):
            value = self._get_value(inst.value)
            print(f"Output: {value}")
            
        elif isinstance(inst, Jump):
            self.current_instruction = self.labels[inst.target] - 1
            
        elif isinstance(inst, ConditionalJump):
            condition = inst.condition.startswith('not ')
            value = self._get_value(inst.condition[4:] if condition else inst.condition)
            if condition != bool(value):
                self.current_instruction = self.labels[inst.target] - 1
                
    # Get value of a variable or literal.
    def _get_value(self, name: str) -> float:
        try:
            return float(name)  # Try to convert to number
        except ValueError:
            if name in self.variables:
                return self.variables[name]
            elif name in self.temporaries:
                return self.temporaries[name]
            else:
                return 0.0  # Default value for undefined variables
            
    # Set value of a variable or temporary.
    def _set_value(self, name: str, value: float) -> None:
        if name.startswith('t'):
            self.temporaries[name] = value
        else:
            self.variables[name] = value
            
    # Apply binary operator.
    def _apply_operator(self, left: float, operator: str, right: float) -> float:
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right if right != 0 else 0
        elif operator == '<=':
            return float(left <= right)
        elif operator == '>=':
            return float(left >= right)
        elif operator == '<':
            return float(left < right)
        elif operator == '>':
            return float(left > right)
        elif operator == '==':
            return float(left == right)
        elif operator == '!=':
            return float(left != right)
        return 0.0
        
    # Apply unary operator.
    def _apply_unary_operator(self, operator: str, operand: float) -> float:
        if operator == '+':
            return operand
        elif operator == '-':
            return -operand
        return 0.0 