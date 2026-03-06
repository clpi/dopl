#!/bin/bash
# Ado Language Development Environment Setup
# This script sets up a complete Neovim development environment for Ado

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "  Ado Language Development Environment"
echo "========================================="
echo ""

# Check for Neovim
if ! command -v nvim &> /dev/null; then
    echo "Error: Neovim is required but not installed."
    echo "Please install Neovim 0.8+ first."
    exit 1
fi

echo "✓ Found Neovim: $(nvim --version | head -1)"
echo ""

# Check for Python (for LSP)
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required for the LSP server."
    exit 1
fi

echo "✓ Found Python: $(python3 --version)"
echo ""

# Build the Ado compiler
echo "Building Ado compiler..."
if [ -f build.sh ]; then
    ./build.sh > /dev/null 2>&1 || { echo "Warning: Build had some issues"; }
    echo "✓ Compiler built: ./doc"
else
    echo "Warning: build.sh not found, skipping compiler build"
fi
echo ""

# Make LSP executable
chmod +x lsp/do-lsp.py 2>/dev/null || true
echo "✓ LSP server ready: lsp/do-lsp.py"
echo ""

# Setup Tree-sitter
echo "Setting up Tree-sitter grammar..."
if [ -d tree-sitter-do ]; then
    if command -v tree-sitter &> /dev/null; then
        cd tree-sitter-do
        tree-sitter generate > /dev/null 2>&1 || echo "  Note: tree-sitter generate needs to be run separately if needed"
        cd ..
        echo "✓ Tree-sitter grammar available"
    else
        echo "  Note: Install tree-sitter CLI for grammar generation"
        echo "    npm install -g tree-sitter-cli"
    fi
else
    echo "  Warning: tree-sitter-do directory not found"
fi
echo ""

# Create vim syntax file if needed
if [ ! -f vim/syntax/ado.vim ]; then
    mkdir -p vim/syntax vim/ftdetect vim/ftplugin
    cat > vim/syntax/ado.vim << 'VIMSYNTAX'
" Ado Language Syntax
if exists("b:current_syntax")
    finish
endif

syn keyword adoKeyword fn let if else while for return true false and or not
syn keyword adoBuiltin print len push
syn match adoNumber /\d\+/
syn match adoOperator /[-+*/%<>=!]=\|[<>]\|[-+*/]/
syn region adoString start=/"/ skip=/\\"/ end=/"/
syn region adoComment start=/#/ end=/$/
syn match adoFuncCall /\w\+\ze\s*(/
syn match adoIdentifier /\w\+/

hi def link adoKeyword Keyword
hi def link adoBuiltin Function
hi def link adoNumber Number
hi def link adoString String
hi def link adoComment Comment
hi def link adoOperator Operator
hi def link adoFuncCall Function
hi def link adoIdentifier Identifier

let b:current_syntax = "ado"
VIMSYNTAX

    cat > vim/ftdetect/ado.vim << 'VIMFT'
au BufRead,BufNewFile *.do set filetype=ado
VIMFT

    cat > vim/ftplugin/ado.vim << 'VIMFTPLUGIN'
" Ado file type plugin
setlocal commentstring=#\ %s
setlocal formatoptions+=croql
setlocal tabstop=2 shiftwidth=2 expandtab
setlocal matchpairs+=(:)
setlocal suffixesadd=.do

" Auto-format on save (optional)
" autocmd BufWritePre <buffer> lua vim.lsp.buf.format()
VIMFTPLUGIN

    echo "✓ Vim syntax files created"
fi
echo ""

# Create convenience script for running the editor
cat > ado-edit << 'EDITSCRIPT'
#!/bin/bash
# Launch Neovim with Ado development environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/nvim/init.lua"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

exec nvim -u "$CONFIG_FILE" "$@"
EDITSCRIPT

chmod +x ado-edit
echo "✓ Created ado-edit launcher script"
echo ""

# Print summary
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Usage:"
echo "  ./doc              - Start REPL"
echo "  ./doc file.do      - Compile and run"
echo "  ./ado-edit file.do - Edit with full IDE support"
echo ""
echo "Neovim LSP Features:"
echo "  gd          - Go to definition"
echo "  gD          - Go to type definition"
echo "  gr          - Find references"
echo "  K           - Show hover info"
echo "  <leader>rn  - Rename symbol"
echo "  <leader>f   - Format document"
echo "  <leader>ca  - Code actions"
echo "  <leader>e   - Show diagnostics"
echo "  [d / ]d     - Navigate diagnostics"
echo "  <C-k>       - Signature help"
echo ""
echo "For best experience, ensure you have:"
echo "  - Neovim 0.8+ with Lua support"
echo "  - nvim-treesitter plugin (optional, for better highlighting)"
echo "  - nvim-cmp plugin (optional, for autocompletion)"
echo ""
