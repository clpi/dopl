# Ado Language Editor Setup

## Quick Start

Launch Neovim with full Ado language support:

```bash
./ado-edit example.do
```

This automatically loads:
- Syntax highlighting
- LSP server (completion, go-to-definition, diagnostics)
- Tree-sitter parser (advanced syntax highlighting)

## Features

### LSP Keybindings

- `gd` - Go to definition
- `gr` - Find references
- `K` - Show hover information
- `<leader>rn` - Rename symbol
- `<leader>f` - Format document
- `<leader>ca` - Code actions

### Tree-sitter

Advanced syntax highlighting and code understanding:
- Semantic highlighting
- Better indentation
- Code folding support

## Prerequisites

### Required
- Neovim 0.8+
- Python 3

### Optional (for Tree-sitter)
- nvim-treesitter plugin
- tree-sitter CLI: `npm install -g tree-sitter-cli`

## Building Tree-sitter Parser

```bash
cd tree-sitter-do
./build.sh
```

## Manual Setup

If you prefer to use your own Neovim config, source the Ado config:

```lua
-- In your init.lua
vim.cmd('source ' .. vim.fn.expand('~/path/to/ado/nvim/init.lua'))
```

Or use it as a reference to integrate into your existing setup.
