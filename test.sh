#!/bin/bash

echo "Testing PL compiler with all examples..."
echo ""

for file in example.do examples/*.do; do
    echo "Running $file:"
    ./doc "$file"
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

echo ""
echo "Checking compiler does not write ./out or ./out.c..."
tmpdir=$(mktemp -d)
cp ./doc "$tmpdir"/
cp ./example.do "$tmpdir"/
(
    cd "$tmpdir" || exit 1
    ./doc example.do >/dev/null
)
if [ -e "$tmpdir/out" ] || [ -e "$tmpdir/out.c" ]; then
    echo "Found insecure output files in working directory!"
    rm -rf "$tmpdir"
    exit 1
fi
rm -rf "$tmpdir"
