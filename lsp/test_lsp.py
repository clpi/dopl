import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lsp import ado_lsp
except ImportError:
    pass

class TestLSP(unittest.TestCase):
    def test_parse(self):
        # We can't easily test without mock, but just creating the instance works as a smoke test
        server = ado_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "fn main() {\n  let a = 1\n}")
        self.assertIn("main", server.symbols)
        self.assertIn("a", server.symbols)

    def test_missing_let_assignment(self):
        server = ado_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "fn main() {\n  let a\n}")
        diags = server.get_diagnostics("file:///test.do", "fn main() {\n  let a\n}")
        self.assertTrue(any(d['message'] == 'let statement requires assignment' for d in diags))

    def test_undefined_function(self):
        server = ado_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "fn main() {\n  foo()\n}")
        diags = server.get_diagnostics("file:///test.do", "fn main() {\n  foo()\n}")
        self.assertTrue(any('Undefined function: foo' in d['message'] for d in diags))

    def test_semantic_tokens(self):
        server = ado_lsp.AdoLSP()
        server.docs["file:///test.do"] = "fn main() {\n  let a = 1\n}"
        server.parse_symbols("file:///test.do", server.docs["file:///test.do"])
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}}}
        result = server.handle_semantic_tokens_full(msg)
        self.assertIn('data', result)
        self.assertTrue(len(result['data']) > 0)

    def test_inlay_hints(self):
        server = ado_lsp.AdoLSP()
        text = "fn add(a, b) {}\nfn main() {\n  add(1, 2)\n}"
        server.docs["file:///test.do"] = text
        server.parse_symbols("file:///test.do", text)
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'range': {'start': {'line': 0}, 'end': {'line': 3}}}}
        hints = server.handle_inlay_hint(msg)
        self.assertTrue(any('a:' in h['label'] for h in hints))

    def test_document_highlight(self):
        server = ado_lsp.AdoLSP()
        text = "fn main() {\n  let a = 1\n  print(a)\n}"
        server.docs["file:///test.do"] = text
        server.parse_symbols("file:///test.do", text)
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'position': {'line': 1, 'character': 7}}}
        highlights = server.handle_document_highlight(msg)
        self.assertEqual(len(highlights), 2)

    def test_code_action(self):
        server = ado_lsp.AdoLSP()
        diag = {'message': 'let statement requires assignment', 'range': {'end': {'line': 1, 'character': 7}}}
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'context': {'diagnostics': [diag]}}}
        actions = server.handle_code_action(msg)
        self.assertTrue(any(a['title'] == 'Initialize variable' for a in actions))

    def test_folding_range(self):
        server = ado_lsp.AdoLSP()
        text = "fn main() {\n  let a = 1\n}"
        server.docs["file:///test.do"] = text
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}}}
        folds = server.handle_folding_range(msg)
        self.assertEqual(len(folds), 1)
        self.assertEqual(folds[0]['startLine'], 0)
        self.assertEqual(folds[0]['endLine'], 2)

    def test_call_hierarchy(self):
        server = ado_lsp.AdoLSP()
        text = "fn foo() {}\nfn main() {\n  foo()\n}"
        server.docs["file:///test.do"] = text
        server.parse_symbols("file:///test.do", text)

        # Prepare
        msg_prep = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'position': {'line': 0, 'character': 4}}}
        prep = server.handle_prepare_call_hierarchy(msg_prep)
        self.assertTrue(len(prep) > 0)

        item = prep[0]

        # Incoming
        msg_in = {'params': {'item': item}}
        incoming = server.handle_call_hierarchy_incoming(msg_in)
        self.assertTrue(any(i['from']['name'] == 'main' for i in incoming))

        # Outgoing
        msg_out = {'params': {'item': prep[0]}}
        msg_out['params']['item'] = server.handle_prepare_call_hierarchy({'params': {'textDocument': {'uri': 'file:///test.do'}, 'position': {'line': 1, 'character': 4}}})[0]
        outgoing = server.handle_call_hierarchy_outgoing(msg_out)
        self.assertTrue(any(o['to']['name'] == 'foo' for o in outgoing))

    def test_initialize(self):
        server = ado_lsp.AdoLSP()
        result = server.handle_initialize({})
        self.assertIn('capabilities', result)
        self.assertTrue(result['capabilities']['completionProvider'])
        self.assertTrue(result['capabilities']['definitionProvider'])

    def test_completion(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}"
        server.parse_symbols(uri, server.docs[uri])
        msg = {'params': {'textDocument': {'uri': uri}}}
        result = server.handle_completion(msg)
        self.assertIn('items', result)
        labels = [item['label'] for item in result['items']]
        self.assertIn('myfunc', labels)
        self.assertIn('myvar', labels)
        self.assertIn('a', labels)
        self.assertIn('print', labels)

    def test_hover(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 3, 'character': 2}}}
        result = server.handle_hover(msg)
        self.assertIsNotNone(result)
        self.assertIn("fn myfunc(a, b)", result['contents']['value'])

    def test_definition(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 3, 'character': 2}}}
        result = server.handle_definition(msg)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['uri'], uri)
        self.assertEqual(result[0]['range']['start']['line'], 0)

    def test_references(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)\nmyfunc(3, 4)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 5}}}
        result = server.handle_references(msg)
        self.assertEqual(len(result), 3)  # Definition + 2 usages

    def test_rename(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)\nmyfunc(3, 4)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 5}, 'newName': 'newfunc'}}
        result = server.handle_rename(msg)
        self.assertIsNotNone(result)
        self.assertIn(uri, result['changes'])
        self.assertEqual(len(result['changes'][uri]), 3)

    def test_destructure_symbols(self):
        server = ado_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "let [a, b, ...rest] = [1, 2, 3]")
        self.assertIn("a", server.symbols)
        self.assertIn("b", server.symbols)
        self.assertIn("rest", server.symbols)

    def test_slice_completion(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "let x = "
        result = server.handle_completion({'params': {'textDocument': {'uri': uri}}})
        labels = [item['label'] for item in result['items']]
        self.assertIn('slice', labels)

    def test_listcomp_completion(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "let x = "
        result = server.handle_completion({'params': {'textDocument': {'uri': uri}}})
        labels = [item['label'] for item in result['items']]
        self.assertIn('listcomp', labels)

    def test_destruct_completion(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "let x = "
        result = server.handle_completion({'params': {'textDocument': {'uri': uri}}})
        labels = [item['label'] for item in result['items']]
        self.assertIn('destruct', labels)

    def test_builtin_hover(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "print(x)"
        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 0}}}
        result = server.handle_hover(msg)
        self.assertIsNotNone(result)
        self.assertIn('print', result['contents']['value'])

    def test_slice_hover(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "slice(arr, 1, 3)"
        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 0}}}
        result = server.handle_hover(msg)
        self.assertIsNotNone(result)
        self.assertIn('slice', result['contents']['value'])

    def test_semantic_tokens_operators(self):
        server = ado_lsp.AdoLSP()
        server.docs["file:///test.do"] = "arr[1..5]"
        server.parse_symbols("file:///test.do", server.docs["file:///test.do"])
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}}}
        result = server.handle_semantic_tokens_full(msg)
        self.assertIn('data', result)

    def test_inlay_hints_for_slice(self):
        server = ado_lsp.AdoLSP()
        text = "let x = arr[1..5]"
        server.docs["file:///test.do"] = text
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'range': {'start': {'line': 0}, 'end': {'line': 1}}}}
        hints = server.handle_inlay_hint(msg)
        self.assertIsInstance(hints, list)

    def test_call_hierarchy_with_slice(self):
        server = ado_lsp.AdoLSP()
        text = "fn main() {\n  let x = arr[1..5]\n}"
        server.docs["file:///test.do"] = text
        server.parse_symbols("file:///test.do", text)
        msg = {'params': {'textDocument': {'uri': 'file:///test.do'}, 'position': {'line': 0, 'character': 4}}}
        prep = server.handle_prepare_call_hierarchy(msg)
        self.assertTrue(len(prep) > 0)


    def test_get_symbol_at_pos_out_of_bounds(self):
        server = ado_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "let a = 1"

        # Test out-of-bounds line
        result = server.get_symbol_at_pos(uri, 100, 0)
        self.assertIsNone(result)

        # Test out-of-bounds column
        result_col = server.get_symbol_at_pos(uri, 0, 100)
        self.assertIsNone(result_col)

if __name__ == '__main__':
    unittest.main()
