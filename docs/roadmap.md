# Ado Language Roadmap

Ado is evolving. Here is a high-level roadmap of planned features and enhancements for future releases.

## Phase 1: Core Language Enhancements

- **Strings as Variables:** Allow strings to be assigned to variables, concatenated, and manipulated.
- **Arrays & Collections:** Introduce basic dynamic arrays or fixed-size lists for storing multiple data points.
- **Floating-Point Arithmetic:** Support for `float` / `double` numbers for complex math.

## Phase 2: Architecture and Tooling

- **Standard Library:** Build a small standard library containing mathematical helpers, string manipulation, and I/O wrappers.
- **Module System:** Allow importing code from other `.do` files using an `import` statement.
- **Package Manager:** A minimal tool to download and share Ado modules.

## Phase 3: Advanced Types and Structures

- **Structs / Records:** Introduce custom types to encapsulate related data.
- **Dictionaries / Maps:** Built-in hash maps for fast data retrieval.
- **Memory Management:** Refine memory management models (currently relying on C's capabilities or static allocation).

## Phase 4: IDE and Ecosystem

- **Debugging Support:** Integrate with GDB/LLDB or introduce a native debugger protocol for IDEs.
- **VS Code Extension:** Publish an official VS Code extension utilizing the existing Ado LSP.
- **WebAssembly Target:** Allow the compiler to output WebAssembly (Wasm) instead of C, enabling Ado to run in the browser.
