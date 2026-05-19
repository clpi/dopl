#!/bin/bash

echo "Testing PL compiler with all examples..."
echo ""

for file in example.do examples/*.do; do
    echo "Running $file:"
    ./doc "$file"
    echo "Result: $?"
    echo ""
done
