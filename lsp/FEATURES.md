# PL Language Server - Feature Showcase

## Overview

The PL Language Server provides comprehensive IDE support through the Language Server Protocol (LSP). It offers real-time code intelligence, diagnostics, and refactoring capabilities.

## Features

### 1. Intelligent Code Completion

**Keywords**: `fn`, `let`, `if`, `else`, `return`

**Function Completion with Snippets**:
```pl
fn add(a, b) {
  return a + b
}

fn main() {
  let x = ad  # Type 'ad' → suggests 'add(${1:a}, ${2:b})'
}
```

### 2. Go to Definition

Jump to where symbols are defined:
- Click on `add(5, 10)` → jumps to `fn add(a, b)`
- Works across files
- Supports functions, variables, and parameters

### 3. Find All References

Find every usage of a symbol:
```pl
fn factorial(n) {  # Definition
  if n <= 1 {
    return 1
  }
  return n * factorial(n - 1)  # Reference 1
}

fn main() {
  return factorial(5)  # Reference 2
}
```

### 4. Hover Information

Hover over any symbol to see:
```
fn add(a, b)

Function definition
```

### 5. Document Symbols / Outline

Provides a structured view of your code:
```
📄 example.do
  ⚡ factorial(n)
  ⚡ main()
  📦 result
```

### 6. Real-time Diagnostics

**Error Detection**:
```pl
fn test() {
  let x  # ❌ Error: let statement requires assignment
}

fn main() {
  undefined_func()  # ⚠️  Warning: Undefined function: undefined_func
}
```

**Brace Matching**:
```pl
fn broken() {
  if x > 0 {
    return 1
  }}  # ❌ Error: Unmatched closing brace
}
```

### 7. Code Formatting

Auto-format with proper indentation:

**Before**:
```pl
fn messy(x){
if x>0{
return x
}
return 0
}
```

**After**:
```pl
fn messy(x) {
  if x > 0 {
    return x
  }
  return 0
}
```

### 8. Symbol Renaming

Rename symbols across all files:
```pl
fn calculate(value) {  # Rename 'value' to 'input'
  return value * 2     # Automatically updates here
}

fn main() {
  return calculate(10)  # Function name stays the same
}
```

### 9. Multi-file Support

The LSP tracks symbols across your entire workspace:

**math.do**:
```pl
fn add(a, b) {
  return a + b
}
```

**main.do**:
```pl
fn main() {
  return add(5, 10)  # Completion works, go-to-definition jumps to math.do
}
```

## Performance

- **Incremental parsing**: Only re-parses changed files
- **Fast symbol lookup**: O(1) symbol table access
- **Minimal memory**: Lightweight Python implementation
- **Real-time**: Sub-millisecond response for most operations

## Editor Integration

### Neovim

All features work out of the box with native LSP:
- `gd` - Go to definition
- `gr` - Find references
- `K` - Hover
- `<leader>rn` - Rename
- `<leader>f` - Format

### VS Code

Full integration with:
- IntelliSense completion
- Peek definition
- Find all references
- Breadcrumbs navigation
- Problems panel

### Other Editors

Works with any LSP-compatible editor:
- Vim (with vim-lsp)
- Emacs (with lsp-mode)
- Sublime Text (with LSP package)
- Kate, Helix, etc.

## Testing

Run the test suite:
```bash
python3 lsp/test_lsp.py
```

Tests all major features:
- ✓ Initialization
- ✓ Document synchronization
- ✓ Completion
- ✓ Go to definition
- ✓ Find references
- ✓ Hover
- ✓ Diagnostics
- ✓ Formatting
- ✓ Shutdown

## Architecture

```
┌─────────────┐
│   Editor    │
└──────┬──────┘
       │ LSP Protocol (JSON-RPC)
┌──────▼──────┐
│  PL LSP     │
│  Server     │
├─────────────┤
│ Symbol      │ ← Functions, variables, parameters
│ Table       │
├─────────────┤
│ Document    │ ← Open files cache
│ Cache       │
├─────────────┤
│ Parser      │ ← Regex-based symbol extraction
└─────────────┘
```

## Future Enhancements

Potential additions:
- Semantic highlighting
- Code actions (quick fixes)
- Inlay hints (parameter names)
- Call hierarchy
- Type inference
- Workspace symbols search
- Code lens (show references inline)
