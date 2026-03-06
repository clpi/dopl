#!/bin/bash
cd "$(dirname "$0")"

if ! command -v tree-sitter &> /dev/null; then
    echo "Error: tree-sitter CLI not found"
    echo "Install with: npm install -g tree-sitter-cli"
    exit 1
fi

echo "Generating Tree-sitter parser..."
tree-sitter generate

echo "Testing grammar..."
tree-sitter test

echo "Tree-sitter grammar built successfully!"
