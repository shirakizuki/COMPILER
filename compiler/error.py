"""
Error handling module for the Mini Compiler.
This module provides error reporting functionality for lexical, syntax, and semantic errors.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CompilerError:
    """Base class for compiler errors."""
    message: str
    line: int
    column: int
    error_type: str
    source_line: Optional[str] = None

class ErrorHandler:
    """
    Handles error collection and reporting for the compiler.
    """
    
    def __init__(self, source_code: str):
        self.source_code = source_code.splitlines()
        self.errors: List[CompilerError] = []
        
    def add_error(self, message: str, line: int, column: int, error_type: str) -> None:
        """Add an error to the collection."""
        source_line = self.source_code[line - 1] if 0 < line <= len(self.source_code) else None
        self.errors.append(CompilerError(message, line, column, error_type, source_line))
        
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
        
    def report_errors(self) -> str:
        """Generate a formatted error report."""
        if not self.errors:
            return "No errors found."
            
        report = []
        for error in sorted(self.errors, key=lambda e: (e.line, e.column)):
            report.append(f"{error.error_type} Error at line {error.line}, column {error.column}:")
            report.append(f"  {error.message}")
            
            if error.source_line:
                report.append(f"  {error.source_line}")
                report.append("  " + " " * (error.column - 1) + "^")
                
            report.append("")
            
        return "\n".join(report)

class ErrorReporter:
    """
    Provides static methods for reporting different types of errors.
    """
    
    @staticmethod
    def lexical_error(handler: ErrorHandler, message: str, line: int, column: int) -> None:
        """Report a lexical error."""
        handler.add_error(message, line, column, "Lexical")
        
    @staticmethod
    def syntax_error(handler: ErrorHandler, message: str, line: int, column: int) -> None:
        """Report a syntax error."""
        handler.add_error(message, line, column, "Syntax")
        
    @staticmethod
    def semantic_error(handler: ErrorHandler, message: str, line: int, column: int) -> None:
        """Report a semantic error."""
        handler.add_error(message, line, column, "Semantic")
        
    @staticmethod
    def type_error(handler: ErrorHandler, message: str, line: int, column: int) -> None:
        """Report a type error."""
        handler.add_error(message, line, column, "Type")
        
    @staticmethod
    def scope_error(handler: ErrorHandler, message: str, line: int, column: int) -> None:
        """Report a scope error."""
        handler.add_error(message, line, column, "Scope") 