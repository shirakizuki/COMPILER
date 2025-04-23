# Mini Compiler

A simple compiler implementation for a custom programming language. This compiler performs lexical analysis, syntax analysis, semantic analysis, and generates intermediate code.

## Components

1. **Lexical Analyzer (Scanner)**
   - Tokenizes input code using regular expressions
   - Identifies keywords, identifiers, literals, operators, etc.

2. **Syntax Analyzer (Parser)**
   - Implements LL(1) parsing
   - Generates Abstract Syntax Tree (AST)

3. **Semantic Analyzer**
   - Performs type checking
   - Validates variable scope
   - Handles error detection

4. **Intermediate Code Generator**
   - Generates Three-Address Code (TAC)
   - Handles basic optimizations

5. **Error Handling**
   - Detects and reports syntax and semantic errors
   - Provides meaningful error messages for debugging

6. **Optimizer**
   - Implements **constant folding** to evaluate constant expressions at compile time
   - Performs **dead code elimination** to remove unreachable or redundant code

7. **Code Generator**
   - Translates intermediate code into low-level assembly-like code
   - Targets a hypothetical machine with simple instructions

## Project Structure

```
.
├── compiler/
│   ├── __init__.py
│   ├── lexer.py        # Lexical Analyzer
│   ├── parser.py       # Syntax Analyzer
│   ├── semantic.py     # Semantic Analyzer
│   ├── intermediate.py # Intermediate Code Generator
│   ├── optimizer.py    # Optimizer (Constant Folding, Dead Code Elimination)
│   ├── codegen.py      # Code Generator
│   └── error.py        # Error Handling
├── tests/
│   └── __init__.py
├── requirements.txt
└── README.md
```

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the compiler with a `.bnrt` file:
```bash
python -m compiler.main input_file.bnrt
```

3. To install the compiler run:
```bash
pip install -e .
```

## Language Features

- Variable declarations
- Basic arithmetic operations
- Conditional statements
- Simple loops
- Type checking
- Error reporting
- Optimizations (constant folding, dead code elimination)
- Low-level code generation for a hypothetical machine