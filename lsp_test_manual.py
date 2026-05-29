from lsp.do_lsp import AdoLSP
import sys

# Mute stdout to not print send output
sys.stdout = open('/dev/null', 'w')
server = AdoLSP()

# Parse a basic document
server.parse_symbols("file:///test.do", "fn foo() {\n  let bar = 1\n}")

# Test completion
comp = server.handle_completion({})
assert len(comp['items']) > 0

# Test symbols
syms = server.handle_document_symbols({'params': {'textDocument': {'uri': 'file:///test.do'}}})
assert len(syms) == 2

print("ok", file=sys.stderr)
