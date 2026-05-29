1. Add `recv` and `send` methods to handle JSON-RPC over stdin/stdout.
2. Implement `handle_initialize` to return server capabilities.
3. Implement `handle_completion` to return completions based on `self.keywords`, `self.builtins`, and symbols in `self.symbols`.
4. Implement `handle_definition` to return the location of the symbol.
5. Implement `handle_references` to return references.
6. Implement `handle_hover` to return documentation (e.g. from `docstring` and signature).
7. Implement `handle_signature_help` to show function signature.
8. Implement `handle_formatting` (a basic format or pass).
9. Implement `handle_rename` and `handle_prepare_rename`.
10. Implement `handle_document_symbols` and `handle_workspace_symbols`.
11. Implement `handle_code_action` and `handle_code_lens` (empty lists for now or basic ones).
