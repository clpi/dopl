# Ado Language Server

Comprehensive LSP server for Ado language providing full IDE support.

## Features

### Code Intelligence
- **Completion**: Keywords, functions with parameter snippets
- **Go to Definition**: Jump to function/variable definitions
- **Find References**: Find all usages of symbols
- **Hover**: Show function signatures and documentation
- **Document Symbols**: Outline view of functions and variables

### Code Quality
- **Diagnostics**: Real-time syntax and semantic error checking
  - Undefined function calls
  - Missing assignments in let statements
  - Unmatched braces
- **Formatting**: Auto-format with proper indentation
- **Rename**: Rename symbols across all files

### Workspace Support
- Multi-file symbol tracking
- Cross-file references
- Workspace-wide symbol search

## Setup for Neovim

Add to your `init.lua`:

```lua
vim.api.nvim_create_autocmd("FileType", {
  pattern = "ado",
  callback = function()
    vim.lsp.start({
      name = "ado-lsp",
      cmd = {vim.fn.expand("~/.local/bin/do-lsp")},
      root_dir = vim.fs.dirname(vim.fs.find({"build.sh"}, { upward = true })[1]),
    })
  end,
})
```

Install the LSP:
```bash
cp lsp/do-lsp.py ~/.local/bin/do-lsp
chmod +x ~/.local/bin/do-lsp
```

## Setup for VS Code

1. Install a generic LSP extension
2. Add to `settings.json`:

```json
{
  "genericLSP.languageServers": {
    "ado": {
      "command": "/path/to/dopl/lsp/do-lsp.py",
      "fileExtensions": ["do"]
    }
  }
}
```

## Usage

The LSP automatically activates when you open `.do` files. Available commands:

- `gd` - Go to definition (Neovim)
- `gr` - Find references (Neovim)
- `K` - Show hover information (Neovim)
- `<leader>rn` - Rename symbol (Neovim)
- `<leader>f` - Format document (Neovim)

## Architecture

The LSP maintains:
- **Document cache**: All open files
- **Symbol table**: Functions, variables, parameters across all files
- **Reference tracking**: Fast lookup of symbol usages

Symbols are re-parsed on every document change for real-time accuracy.
