#!/usr/bin/env python3
"""
Script to run the Mini Compiler.
"""

import sys
from compiler.main import main

if __name__ == '__main__':
    sys.path.insert(0, '.')  # Add current directory to Python path
    main() 