#!/bin/bash

echo "Testing Ado compiler with all examples..."
echo ""

passed=0
failed=0
failed_files=""

for file in example.do examples/*.do; do
    echo "Running $file..."
    ./doc "$file" >/dev/null 2>&1
    ret=$?
    if [ $ret -eq 0 ]; then
        echo "  PASSED"
        passed=$((passed + 1))
    else
        echo "  FAILED (exit $ret)"
        failed=$((failed + 1))
        failed_files="$failed_files $file"
    fi
    echo ""
done

echo "========================================="
echo "Results: $passed passed, $failed failed"
if [ $failed -gt 0 ]; then
    echo "Failed files:$failed_files"
fi
echo "========================================="

echo ""
echo "Running C unit tests..."
if cc -o test_main test_main.c lexer.c parser.c codegen.c; then
    ./test_main
    res=$?
    if [ $res -ne 0 ]; then
        echo "C unit tests failed!"
    fi
else
    echo "Failed to compile C unit tests!"
    exit 1
fi
