"""
Main module for the Mini Compiler.
This module ties together all compiler components and provides the main interface.
"""

import sys
import traceback
from typing import List, Optional
from .lexer import Lexer, LexicalError, Token, TokenType
from .parser import Parser, ParseError
from .semantic import SemanticAnalyzer, SemanticError
from .intermediate import IntermediateCodeGenerator, TACInstruction
from .interpreter import Interpreter
from .error import ErrorHandler, ErrorReporter

class Compiler:
    """
    Main compiler class that coordinates all compilation phases.
    """
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.error_handler = ErrorHandler(source_code)
        
    def compile(self) -> Optional[List[TACInstruction]]:
        """
        Compile the source code through all phases.
        Returns the generated intermediate code if successful, None if errors occurred.
        """
        try:
            print("\nStarting lexical analysis...")
            # Lexical Analysis
            lexer = Lexer(self.source_code)
            tokens = lexer.tokenize()
            print(f"Found {len(tokens)} tokens")
            print("\nTokens:")
            for token in tokens:
                print(f"  {token}")
            
            print("\nStarting syntax analysis...")
            # Syntax Analysis
            parser = Parser(tokens)
            ast = parser.parse()
            print("AST generated successfully")
            
            print("\nStarting semantic analysis...")
            # Semantic Analysis
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            print("Semantic analysis completed")
            
            print("\nGenerating intermediate code...")
            # Intermediate Code Generation
            generator = IntermediateCodeGenerator()
            intermediate_code = generator.generate(ast)
            
            print("\nOptimizing code...")
            # Optimization
            generator.optimize()
            print("Optimization completed")
            
            return intermediate_code
            
        except LexicalError as e:
            print(f"\nLexical Error: {str(e)}")
            print(f"Line {e.line}, Column {e.column}")
            ErrorReporter.lexical_error(self.error_handler, str(e), e.line, e.column)
        except ParseError as e:
            print(f"\nParse Error: {str(e)}")
            print(f"Line {e.line}, Column {e.column}")
            ErrorReporter.syntax_error(self.error_handler, str(e), e.line, e.column)
        except SemanticError as e:
            print(f"\nSemantic Error: {str(e)}")
            print(f"Line {e.line}, Column {e.column}")
            ErrorReporter.semantic_error(self.error_handler, str(e), e.line, e.column)
        except Exception as e:
            print(f"\nUnexpected Error: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            # Unexpected errors
            ErrorReporter.semantic_error(
                self.error_handler,
                f"Internal compiler error: {str(e)}",
                0,
                0
            )
            
        return None

def format_tac(instructions: List[TACInstruction]) -> str:
    """Format TAC instructions for output."""
    lines = []
    for i, inst in enumerate(instructions):
        if hasattr(inst, 'name'):  # Label
            lines.append(f"{inst.name}:")
        else:
            lines.append(f"{i:4d}: {str(inst)}")
    return "\n".join(lines)

def main() -> None:
    """Main entry point for the compiler."""
    if len(sys.argv) != 2:
        print("Usage: python -m compiler.main <source_file>")
        sys.exit(1)
        
    try:
        print(f"Reading source file: {sys.argv[1]}")
        with open(sys.argv[1], 'r') as f:
            source_code = f.read()
        print(f"Source code length: {len(source_code)} characters")
        print("\nSource code:")
        print("-" * 40)
        print(source_code)
        print("-" * 40)
    except IOError as e:
        print(f"Error reading source file: {e}")
        sys.exit(1)
        
    compiler = Compiler(source_code)
    intermediate_code = compiler.compile()
    
    if compiler.error_handler.has_errors():
        print("\nCompilation failed with errors:")
        print(compiler.error_handler.report_errors())
        sys.exit(1)
        
    if intermediate_code:
        print("\nCompilation successful!")
        print("\nGenerated Three-Address Code:")
        print("-" * 40)
        print(format_tac(intermediate_code))
        print("-" * 40)
        print("\nProgram output:")
        print("-" * 40)
        interpreter = Interpreter()
        interpreter.execute(intermediate_code)
        print("-" * 40)
    else:
        print("\nCompilation failed with errors.")
        sys.exit(1)

if __name__ == '__main__':
    main() 