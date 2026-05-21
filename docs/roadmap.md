# Ado Roadmap

Ado is currently a minimal programming language focusing on core concepts, high performance via C compilation, and robust IDE support. The development of Ado is ongoing.

## Current Status (v0.1)

- ✅ Core syntax: Functions, variables, if/else, while loops
- ✅ Mathematical and Logical operators
- ✅ Compilation to optimized C code
- ✅ Comprehensive Language Server Protocol (LSP) implementation
- ✅ Neovim IDE integration script
- ✅ Basic I/O (`print`)

## Planned Features

*Note: The following features are planned for future releases. The exact timeline is subject to change.*

### Short-Term Goals
- **Strings and Arrays**: Introduce support for string manipulation and array data structures.
- **Enhanced Type System**: Move beyond integers and booleans to support floats, characters, and potentially simple user-defined types (structs).
- **Standard Library Expansion**: Add built-in functions for file I/O, math utilities, and basic system interactions.
- **Module System**: Allow code to be split across multiple files and imported via an `import` or `include` statement.

### Mid-Term Goals
- **Memory Management**: Implement automatic memory management (e.g., Garbage Collection or ARC) or provide robust manual tools as data structures become more complex.
- **Error Handling**: Introduce a formal error handling mechanism (e.g., `try/catch` or Result types).
- **Package Manager**: A simple package manager to download, share, and build Ado projects and libraries.

### Long-Term Vision
- **Self-Hosting Compiler**: Rewrite the `doc` compiler in Ado itself.
- **Expanded Target Backends**: Support compiling to LLVM IR or WebAssembly (Wasm) in addition to C.
- **Concurrency**: Native support for threads or asynchronous programming.
