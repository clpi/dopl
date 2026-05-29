import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lsp import do_lsp
except ImportError:
    pass

class TestLSP(unittest.TestCase):
    def setUp(self):
        self.server = do_lsp.AdoLSP()
        # Mock sys.stdout to prevent JSON-RPC output during tests
        self.server.send = lambda msg: None

    def test_parse(self):
        self.server.parse_symbols("file:///test.do", "fn main() {\n  let a = 1\n}")
        self.assertIn("main", self.server.symbols)
        self.assertIn("a", self.server.symbols)

    def test_handle_completion(self):
        self.server.parse_symbols("file:///test.do", "fn foo() {}")
        res = self.server.handle_completion({})
        labels = [item['label'] for item in res['items']]
        self.assertIn("fn", labels) # keywords
        self.assertIn("foo", labels) # symbols

    def test_handle_definition(self):
        self.server.docs["file:///test.do"] = "fn bar() {}\nbar()"
        self.server.parse_symbols("file:///test.do", self.server.docs["file:///test.do"])
        msg = {
            'params': {
                'textDocument': {'uri': 'file:///test.do'},
                'position': {'line': 1, 'character': 1} # on 'b' in 'bar()'
            }
        }
        res = self.server.handle_definition(msg)
        self.assertIsNotNone(res)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['uri'], 'file:///test.do')
        self.assertEqual(res[0]['range']['start']['line'], 0) # definition is on line 0

    def test_handle_hover(self):
        self.server.docs["file:///test.do"] = "# Does something\nfn test_hover() {}"
        self.server.parse_symbols("file:///test.do", self.server.docs["file:///test.do"])
        msg = {
            'params': {
                'textDocument': {'uri': 'file:///test.do'},
                'position': {'line': 1, 'character': 4}
            }
        }
        res = self.server.handle_hover(msg)
        self.assertIsNotNone(res)
        self.assertIn("Does something", res['contents']['value'])
        self.assertIn("test_hover", res['contents']['value'])

    def test_handle_document_symbols(self):
        self.server.parse_symbols("file:///test.do", "fn a() {}\nlet b = 1")
        res = self.server.handle_document_symbols({'params': {'textDocument': {'uri': 'file:///test.do'}}})
        self.assertEqual(len(res), 2)
        names = [sym['name'] for sym in res]
        self.assertIn("a", names)
        self.assertIn("b", names)

if __name__ == '__main__':
    unittest.main()
