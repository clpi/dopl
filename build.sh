#!/bin/bash

# Build the Ado compiler with optimizations
echo "Building Ado compiler..."
cc -O2 -o doc main.c lexer.c parser.c codegen.c

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Compiler built: ./doc"
echo ""
echo "Usage:"
echo "  ./doc              # Start REPL"
echo "  ./doc file.do      # Compile and run file"
echo "  ./doc -i file.do   # Run file, then enter REPL"
echo ""
echo "Running example.do..."
echo "====================="
./doc example.do
