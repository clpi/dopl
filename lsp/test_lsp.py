import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lsp import do_lsp
except ImportError:
    pass

class TestLSP(unittest.TestCase):
    def test_parse(self):
        # We can't easily test without mock, but just creating the instance works as a smoke test
        server = do_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "fn main() {\n  let a = 1\n}")
        self.assertIn("main", server.symbols)
        self.assertIn("a", server.symbols)

    def test_initialize(self):
        server = do_lsp.AdoLSP()
        result = server.handle_initialize({})
        self.assertIn('capabilities', result)
        self.assertTrue(result['capabilities']['completionProvider'])
        self.assertTrue(result['capabilities']['definitionProvider'])

    def test_completion(self):
        server = do_lsp.AdoLSP()
        server.parse_symbols("file:///test.do", "fn myfunc(a, b) {\n  let myvar = 1\n}")
        result = server.handle_completion({})
        self.assertIn('items', result)
        labels = [item['label'] for item in result['items']]
        self.assertIn('myfunc', labels)
        self.assertIn('myvar', labels)
        self.assertIn('a', labels)
        self.assertIn('print', labels)

    def test_hover(self):
        server = do_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 3, 'character': 2}}}
        result = server.handle_hover(msg)
        self.assertIsNotNone(result)
        self.assertIn("fn myfunc(a, b)", result['contents']['value'])

    def test_definition(self):
        server = do_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 3, 'character': 2}}}
        result = server.handle_definition(msg)
        self.assertIsNotNone(result)
        self.assertEqual(result['uri'], uri)
        self.assertEqual(result['range']['start']['line'], 0)

    def test_references(self):
        server = do_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)\nmyfunc(3, 4)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 5}}}
        result = server.handle_references(msg)
        self.assertEqual(len(result), 3) # Definition + 2 usages

    def test_rename(self):
        server = do_lsp.AdoLSP()
        uri = "file:///test.do"
        server.docs[uri] = "fn myfunc(a, b) {\n  let myvar = 1\n}\nmyfunc(1, 2)\nmyfunc(3, 4)"
        server.parse_symbols(uri, server.docs[uri])

        msg = {'params': {'textDocument': {'uri': uri}, 'position': {'line': 0, 'character': 5}, 'newName': 'newfunc'}}
        result = server.handle_rename(msg)
        self.assertIsNotNone(result)
        self.assertIn(uri, result['changes'])
        self.assertEqual(len(result['changes'][uri]), 3)

if __name__ == '__main__':
    unittest.main()
