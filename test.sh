#!/bin/bash

echo "Testing PL compiler with all examples..."
echo ""

for file in example.do examples/*.do; do
    echo "Running $file:"
    ./plc "$file"
    echo "Result: $?"
    echo ""
done

echo "Running C unit tests..."
cc -o test_main test_main.c lexer.c parser.c codegen.c
if [ $? -eq 0 ]; then
    ./test_main
    res=$?
    if [ $res -ne 0 ]; then
        echo "C unit tests failed!"
    fi
else
    echo "Failed to compile C unit tests!"
    exit 1
fi
