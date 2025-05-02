"""
Code Generator for the Mini Compiler.
This module generates assembly code for a hypothetical machine from Three-Address Code (TAC).
"""

from typing import List
from .intermediate import (
    TACInstruction, Assignment, BinaryOperation, UnaryOperation,
    Print, Jump, ConditionalJump, Label
)

class AssemblyGenerator:
    """
    Generates assembly code for a hypothetical machine.
    The hypothetical machine has:
    - 8 general-purpose registers (R0-R7)
    - A stack for function calls and local variables
    - Basic arithmetic and comparison operations
    - Jump and conditional jump instructions
    - Load/store instructions for memory access
    """
    
    def __init__(self):
        self.assembly_code: List[str] = []
        self.register_pool = set(f"R{i}" for i in range(8))
        self.used_registers = set()
        self.label_map = {}  # Maps TAC labels to assembly labels
        
    def generate(self, tac_instructions: List[TACInstruction]) -> List[str]:
        """Generate assembly code from TAC instructions."""
        # First pass: collect labels
        for inst in tac_instructions:
            if isinstance(inst, Label):
                self.label_map[inst.name] = f"L{len(self.label_map)}"
        
        # Second pass: generate code
        for inst in tac_instructions:
            if isinstance(inst, Assignment):
                self._generate_assignment(inst)
            elif isinstance(inst, BinaryOperation):
                self._generate_binary_op(inst)
            elif isinstance(inst, UnaryOperation):
                self._generate_unary_op(inst)
            elif isinstance(inst, Print):
                self._generate_print(inst)
            elif isinstance(inst, Jump):
                self._generate_jump(inst)
            elif isinstance(inst, ConditionalJump):
                self._generate_conditional_jump(inst)
            elif isinstance(inst, Label):
                self._generate_label(inst)
                
        return self.assembly_code
        
    def _get_register(self) -> str:
        """Get an available register."""
        if not self.register_pool:
            raise RuntimeError("No available registers")
        reg = self.register_pool.pop()
        self.used_registers.add(reg)
        return reg
        
    def _free_register(self, reg: str) -> None:
        """Free a register."""
        if reg in self.used_registers:
            self.used_registers.remove(reg)
            self.register_pool.add(reg)
            
    def _generate_assignment(self, inst: Assignment) -> None:
        """Generate code for assignment."""
        # Try to load the source value into a register
        try:
            # If source is a number, use immediate load
            value = float(inst.source)
            reg = self._get_register()
            self.assembly_code.append(f"    LOAD {reg}, #{value}")
        except ValueError:
            # If source is a variable, load from memory
            reg = self._get_register()
            self.assembly_code.append(f"    LOAD {reg}, {inst.source}")
            
        # Store the value in the target variable
        self.assembly_code.append(f"    STORE {reg}, {inst.target}")
        self._free_register(reg)
        
    def _generate_binary_op(self, inst: BinaryOperation) -> None:
        """Generate code for binary operation."""
        # Get registers for operands
        left_reg = self._get_register()
        right_reg = self._get_register()
        result_reg = self._get_register()
        
        # Load operands
        try:
            left_val = float(inst.left)
            self.assembly_code.append(f"    LOAD {left_reg}, #{left_val}")
        except ValueError:
            self.assembly_code.append(f"    LOAD {left_reg}, {inst.left}")
            
        try:
            right_val = float(inst.right)
            self.assembly_code.append(f"    LOAD {right_reg}, #{right_val}")
        except ValueError:
            self.assembly_code.append(f"    LOAD {right_reg}, {inst.right}")
            
        # Generate operation
        if inst.operator == '+':
            self.assembly_code.append(f"    ADD {result_reg}, {left_reg}, {right_reg}")
        elif inst.operator == '-':
            self.assembly_code.append(f"    SUB {result_reg}, {left_reg}, {right_reg}")
        elif inst.operator == '*':
            self.assembly_code.append(f"    MUL {result_reg}, {left_reg}, {right_reg}")
        elif inst.operator == '/':
            self.assembly_code.append(f"    DIV {result_reg}, {left_reg}, {right_reg}")
        elif inst.operator in ['<', '<=', '>', '>=', '==', '!=']:
            self.assembly_code.append(f"    CMP {left_reg}, {right_reg}")
            self.assembly_code.append(f"    SET{inst.operator} {result_reg}")
            
        # Store result
        self.assembly_code.append(f"    STORE {result_reg}, {inst.target}")
        
        # Free registers
        self._free_register(left_reg)
        self._free_register(right_reg)
        self._free_register(result_reg)
        
    def _generate_unary_op(self, inst: UnaryOperation) -> None:
        """Generate code for unary operation."""
        # Get registers
        operand_reg = self._get_register()
        result_reg = self._get_register()
        
        # Load operand
        try:
            operand_val = float(inst.operand)
            self.assembly_code.append(f"    LOAD {operand_reg}, #{operand_val}")
        except ValueError:
            self.assembly_code.append(f"    LOAD {operand_reg}, {inst.operand}")
            
        # Generate operation
        if inst.operator == '-':
            self.assembly_code.append(f"    NEG {result_reg}, {operand_reg}")
        elif inst.operator == '+':
            self.assembly_code.append(f"    MOV {result_reg}, {operand_reg}")
            
        # Store result
        self.assembly_code.append(f"    STORE {result_reg}, {inst.target}")
        
        # Free registers
        self._free_register(operand_reg)
        self._free_register(result_reg)
        
    def _generate_print(self, inst: Print) -> None:
        """Generate code for print statement."""
        reg = self._get_register()
        try:
            value = float(inst.value)
            self.assembly_code.append(f"    LOAD {reg}, #{value}")
        except ValueError:
            self.assembly_code.append(f"    LOAD {reg}, {inst.value}")
        self.assembly_code.append(f"    PRINT {reg}")
        self._free_register(reg)
        
    def _generate_jump(self, inst: Jump) -> None:
        """Generate code for unconditional jump."""
        self.assembly_code.append(f"    JMP {self.label_map[inst.target]}")
        
    def _generate_conditional_jump(self, inst: ConditionalJump) -> None:
        """Generate code for conditional jump."""
        reg = self._get_register()
        try:
            value = float(inst.condition)
            self.assembly_code.append(f"    LOAD {reg}, #{value}")
        except ValueError:
            self.assembly_code.append(f"    LOAD {reg}, {inst.condition}")
        self.assembly_code.append(f"    JZ {reg}, {self.label_map[inst.target]}")
        self._free_register(reg)
        
    def _generate_label(self, inst: Label) -> None:
        """Generate code for label."""
        self.assembly_code.append(f"{self.label_map[inst.name]}:") 