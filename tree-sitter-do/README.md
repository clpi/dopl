# Tree-sitter Grammar for DO Language

Tree-sitter parser for the DO programming language, providing advanced syntax highlighting and code understanding.

## Features

- Full syntax tree parsing
- Semantic highlighting
- Code folding support
- Better indentation
- Fast incremental parsing

## Building

```bash
./build.sh
```

Requirements:
- Node.js
- tree-sitter CLI: `npm install -g tree-sitter-cli`

## Grammar Rules

The grammar supports:

- **Functions**: `fn name(params) { body }`
- **Variables**: `let name = value`
- **Control flow**: `if condition { } else { }`
- **Expressions**: Binary operations, function calls
- **Literals**: Numbers, identifiers

## Highlight Queries

Located in `queries/highlights.scm`:

- Keywords: `fn`, `let`, `if`, `else`, `return`
- Functions: Function names and calls
- Variables: Parameters and let bindings
- Operators: Arithmetic and comparison
- Literals: Numbers
- Punctuation: Brackets and delimiters

## Integration

### Neovim

Use the provided `do-edit` script, or manually:

```lua
local parser_config = require('nvim-treesitter.parsers').get_parser_configs()
parser_config.do_lang = {
  install_info = {
    url = '/path/to/tree-sitter-do',
    files = {'src/parser.c'},
  },
  filetype = 'do',
}
```

### Other Editors

- **Helix**: Add to `languages.toml`
- **Emacs**: Use `tree-sitter-langs`
- **VS Code**: Use tree-sitter extension

## Testing

```bash
tree-sitter test
```

Add test cases in `test/corpus/` directory.

## Grammar Structure

```
source_file
├── function_declaration
│   ├── name: identifier
│   ├── parameter_list
│   └── body: block
├── let_statement
│   ├── name: identifier
│   └── value: expression
├── if_statement
│   ├── condition: expression
│   ├── consequence: block
│   └── alternative: block (optional)
└── return_statement
    └── expression
```
