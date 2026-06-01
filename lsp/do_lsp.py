#!/usr/bin/env python3
"""
Ado Language Server Protocol Implementation
Full-featured LSP for the Ado programming language
"""
import json
import sys
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class Symbol:
    name: str
    kind: str
    uri: str
    line: int
    col: int
    end_line: int
    end_col: int
    params: List[str] = field(default_factory=list)
    docstring: str = ""

@dataclass
class Reference:
    uri: str
    line: int
    col: int
    end_col: int

class AdoLSP:
    def __init__(self):
        self.docs: Dict[str, str] = {}
        self.symbols: Dict[str, List[Symbol]] = {}
        self.keywords = ['fn', 'let', 'if', 'else', 'while', 'for', 'return',
                         'true', 'false', 'and', 'or', 'not', 'print', 'len', 'push']
        self.builtins = ['print', 'len', 'push']

    def parse_symbols(self, uri: str, text: str):
        symbols = []
        lines = text.split('\n')
        fn_pattern = re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)')
        let_pattern = re.compile(r'let\s+(\w+)\s*=')

        brace_count = 0
        active_functions = []

        for i, line in enumerate(lines):
            match = fn_pattern.search(line)
            if match:
                name = match.group(1)
                params_str = match.group(2)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                col = match.start(1)
                docstring = ""
                for k in range(i-1, -1, -1):
                    if lines[k].strip().startswith('#'):
                        docstring = lines[k].strip()[1:].strip() + " " + docstring
                    elif lines[k].strip() == "": continue
                    else: break

                sym = Symbol(name=name, kind='function', uri=uri,
                    line=i, col=col, end_line=i, end_col=len(line),
                    params=params, docstring=docstring.strip())
                symbols.append(sym)

                active_functions.append({
                    'symbol': sym,
                    'started': False,
                    'base_count': brace_count
                })

                for param in params:
                    param_pattern = re.compile(r'\b' + re.escape(param) + r'\b')
                    param_match = param_pattern.search(line)
                    if param_match:
                        symbols.append(Symbol(name=param, kind='parameter', uri=uri,
                            line=i, col=param_match.start(), end_line=i, end_col=param_match.end()))

            if '{' in line:
                for func_data in active_functions:
                    if not func_data['started']:
                        func_data['started'] = True
                        func_data['base_count'] = brace_count

            brace_count += line.count('{') - line.count('}')

            if active_functions:
                remaining_functions = []
                for func_data in active_functions:
                    if func_data['started'] and brace_count == func_data['base_count']:
                        func_data['symbol'].end_line = i
                        func_data['symbol'].end_col = len(line)
                    else:
                        remaining_functions.append(func_data)
                active_functions = remaining_functions

        for i, line in enumerate(lines):
            match = let_pattern.search(line)
            if match:
                symbols.append(Symbol(name=match.group(1), kind='variable', uri=uri,
                    line=i, col=match.start(1), end_line=i, end_col=match.end(1)))

        for sym in symbols:
            if sym.name not in self.symbols: self.symbols[sym.name] = []
            self.symbols[sym.name] = [s for s in self.symbols[sym.name] if s.uri != uri]
            self.symbols[sym.name].append(sym)
    def get_diagnostics(self, uri: str, text: str) -> List[dict]:
        diagnostics = []
        # First check for unbalanced braces just in case
        lines = text.split('\n')
        brace_stack = []
        paren_stack = []
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char == '{': brace_stack.append((i, j))
                elif char == '}':
                    if brace_stack: brace_stack.pop()
                    else: diagnostics.append({'range': {'start': {'line': i, 'character': j},
                        'end': {'line': i, 'character': j+1}}, 'severity': 1,
                        'message': 'Unexpected closing brace', 'source': 'ado-lsp'})
                elif char == '(': paren_stack.append((i, j))
                elif char == ')':
                    if paren_stack: paren_stack.pop()
                    else: diagnostics.append({'range': {'start': {'line': i, 'character': j},
                        'end': {'line': i, 'character': j+1}}, 'severity': 1,
                        'message': 'Unexpected closing parenthesis', 'source': 'ado-lsp'})
        if brace_stack:
            i, j = brace_stack.pop()
            diagnostics.append({'range': {'start': {'line': i, 'character': j},
                'end': {'line': i, 'character': j+1}}, 'severity': 1,
                'message': 'Unmatched opening brace', 'source': 'ado-lsp'})

        if paren_stack:
            i, j = paren_stack.pop()
            diagnostics.append({'range': {'start': {'line': i, 'character': j},
                'end': {'line': i, 'character': j+1}}, 'severity': 1,
                'message': 'Unclosed parenthesis', 'source': 'ado-lsp'})
        return diagnostics




    def recv(self) -> Optional[dict]:
        try:
            line = sys.stdin.readline()
            if not line:
                return None

            if not line.startswith("Content-Length: "):
                # Skip invalid headers
                while line and line.strip():
                    line = sys.stdin.readline()
                return None

            length = int(line[16:].strip())
            if length < 0 or length > 10_000_000:  # 10MB limit
                return None

            # Read until empty line (end of headers)
            while line and line.strip():
                line = sys.stdin.readline()

            content = sys.stdin.read(length)
            if not content:
                return None

            return json.loads(content)
        except Exception:
            return None

    def send(self, msg: dict):
        try:
            content = json.dumps(msg)
            sys.stdout.write(f"Content-Length: {len(content)}\r\n\r\n{content}")
            sys.stdout.flush()
        except Exception:
            pass

    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})

    def get_symbol_at_pos(self, uri: str, line: int, col: int) -> Optional[str]:
        text = self.docs.get(uri)
        if not text:
            return None
        lines = text.split('\n')
        if line >= len(lines):
            return None

        ltext = lines[line]
        if col >= len(ltext):
            return None

        # Find word boundaries around col
        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'):
            start -= 1

        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'):
            end += 1

        word = ltext[start:end]
        return word if word else None

    def handle_definition(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word or word not in self.symbols:
            return []

        sym = self.symbols[word][0] # Just grab the first one for now
        return [{
            'uri': sym.uri,
            'range': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.end_line, 'character': sym.end_col}
            }
        }]

    def find_references(self, word: str) -> List[dict]:
        refs = []
        for doc_uri, text in self.docs.items():
            lines = text.split('\n')
            for i, line in enumerate(lines):
                # Simple regex word boundary match to find references
                pattern = re.compile(r'\b' + re.escape(word) + r'\b')
                for match in pattern.finditer(line):
                    refs.append({
                        'uri': doc_uri,
                        'range': {
                            'start': {'line': i, 'character': match.start()},
                            'end': {'line': i, 'character': match.end()}
                        }
                    })
        return refs

    def handle_references(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word:
            return []

        return self.find_references(word)

    def handle_hover(self, msg: dict) -> Optional[dict]:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word or word not in self.symbols:
            return None

        sym = self.symbols[word][0]

        if sym.kind == 'function':
            hover_text = f"```ado\nfn {sym.name}({', '.join(sym.params)})\n```"
            if sym.docstring:
                hover_text += f"\n\n{sym.docstring}"
        elif sym.kind == 'variable':
            hover_text = f"```ado\nlet {sym.name}\n```"
        else:
            hover_text = f"```ado\n{sym.name}\n```"

        return {
            'contents': {
                'kind': 'markdown',
                'value': hover_text
            }
        }

    def handle_signature_help(self, msg: dict) -> Optional[dict]:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        text = self.docs.get(uri)
        if not text: return None

        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line][:col]

        # Simple heuristic: find the last function call before cursor
        # Not perfect but works for simple cases
        call_match = list(re.finditer(r'(\w+)\s*\(', ltext))
        if not call_match: return None

        func_name = call_match[-1].group(1)
        if func_name not in self.symbols: return None

        sym = self.symbols[func_name][0]
        if sym.kind != 'function': return None

        # Count commas to figure out active parameter
        args_text = ltext[call_match[-1].end():]
        active_param = args_text.count(',')

        parameters = [{'label': p} for p in sym.params]

        return {
            'signatures': [{
                'label': f"{sym.name}({', '.join(sym.params)})",
                'documentation': sym.docstring,
                'parameters': parameters
            }],
            'activeSignature': 0,
            'activeParameter': min(active_param, max(0, len(sym.params) - 1))
        }

    def handle_formatting(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri)
        if not text: return []

        lines = text.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # Decrease indent for closing brace
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)

            formatted_lines.append("  " * indent_level + stripped)

            # Increase indent for opening brace
            if stripped.endswith('{'):
                indent_level += 1

        new_text = '\n'.join(formatted_lines)
        if new_text == text: return []

        return [{
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': len(lines), 'character': 0}
            },
            'newText': new_text
        }]

    def handle_prepare_rename(self, msg: dict) -> Optional[dict]:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word or word in self.keywords or word in self.builtins: return None

        # Simple word boundaries to find the range
        text = self.docs.get(uri, "")
        lines = text.split('\n')
        if line >= len(lines): return None

        ltext = lines[line]
        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1

        return {
            'range': {
                'start': {'line': line, 'character': start},
                'end': {'line': line, 'character': end}
            },
            'placeholder': word
        }

    def handle_rename(self, msg: dict) -> Optional[dict]:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']
        new_name = msg['params']['newName']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word: return None

        refs = self.find_references(word)
        if not refs: return None

        changes = {}
        for ref in refs:
            r_uri = ref['uri']
            if r_uri not in changes:
                changes[r_uri] = []
            changes[r_uri].append({
                'range': ref['range'],
                'newText': new_name
            })

        return {'changes': changes}

    def handle_document_symbols(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        symbols = []
        for name, sym_list in self.symbols.items():
            for sym in sym_list:
                if sym.uri == uri:
                    symbols.append({
                        'name': name,
                        'kind': 12 if sym.kind == 'function' else 13, # Function or Variable
                        'location': {
                            'uri': uri,
                            'range': {
                                'start': {'line': sym.line, 'character': sym.col},
                                'end': {'line': sym.end_line, 'character': sym.end_col}
                            }
                        }
                    })
        return symbols

    def handle_workspace_symbols(self, msg: dict) -> list:
        query = msg['params'].get('query', '').lower()
        symbols = []
        for name, sym_list in self.symbols.items():
            if query and query not in name.lower():
                continue
            for sym in sym_list:
                symbols.append({
                    'name': name,
                    'kind': 12 if sym.kind == 'function' else 13, # Function or Variable
                    'location': {
                        'uri': sym.uri,
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}
                        }
                    }
                })
        return symbols

    def handle_code_action(self, msg: dict) -> list:
        # Minimal empty implementation for now
        return []

    def handle_code_lens(self, msg: dict) -> list:
        # Minimal empty implementation for now
        return []

    def handle_completion(self, msg: dict) -> dict:
        uri = msg['params']['textDocument']['uri']
        items = []

        # Add keywords
        for kw in self.keywords:
            items.append({
                'label': kw,
                'kind': 14, # Keyword
                'detail': 'keyword'
            })

        # Add symbols
        for name, sym_list in self.symbols.items():
            sym = sym_list[0]
            if sym.kind == 'function':
                # Snippet completion for functions
                snippet = name + '(' + ', '.join([f'${{{i+1}:{p}}}' for i, p in enumerate(sym.params)]) + ')'
                items.append({
                    'label': name,
                    'kind': 3, # Function
                    'detail': f'fn {name}({", ".join(sym.params)})',
                    'insertText': snippet,
                    'insertTextFormat': 2, # Snippet
                    'documentation': sym.docstring
                })
            else:
                items.append({
                    'label': name,
                    'kind': 6 if sym.kind == 'variable' else 5, # Variable or Field
                    'detail': sym.kind
                })

        return {'isIncomplete': False, 'items': items}

    def handle_initialize(self, msg: dict) -> dict:
        return {
            'capabilities': {
                'textDocumentSync': 1,  # Full sync
                'completionProvider': {
                    'resolveProvider': False,
                    'triggerCharacters': ['.']
                },
                'definitionProvider': True,
                'referencesProvider': True,
                'hoverProvider': True,
                'documentSymbolProvider': True,
                'workspaceSymbolProvider': True,
                'documentFormattingProvider': True,
                'documentRangeFormattingProvider': True,
                'renameProvider': {
                    'prepareProvider': True
                },
                'signatureHelpProvider': {
                    'triggerCharacters': ['(', ',']
                },
                'codeActionProvider': True,
                'codeLensProvider': {
                    'resolveProvider': False
                }
            }
        }

    def run(self):
        while True:
            try:
                msg = self.recv()
                if msg is None: break
                method = msg.get('method', '')
                result = None
                if method == 'initialize': result = self.handle_initialize(msg)
                elif method == 'initialized': pass
                elif method == 'textDocument/didOpen':
                    uri = msg['params']['textDocument']['uri']
                    self.docs[uri] = msg['params']['textDocument']['text']
                    self.parse_symbols(uri, self.docs[uri])
                    self.publish_diagnostics(uri)
                elif method == 'textDocument/didChange':
                    uri = msg['params']['textDocument']['uri']
                    self.docs[uri] = msg['params']['contentChanges'][0]['text']
                    self.parse_symbols(uri, self.docs[uri])
                    self.publish_diagnostics(uri)
                elif method == 'textDocument/completion': result = self.handle_completion(msg)
                elif method == 'textDocument/definition': result = self.handle_definition(msg)
                elif method == 'textDocument/typeDefinition': result = self.handle_definition(msg)
                elif method == 'textDocument/references': result = self.handle_references(msg)
                elif method == 'textDocument/hover': result = self.handle_hover(msg)
                elif method == 'textDocument/signatureHelp': result = self.handle_signature_help(msg)
                elif method == 'textDocument/formatting': result = self.handle_formatting(msg)
                elif method == 'textDocument/rangeFormatting': result = self.handle_formatting(msg)
                elif method == 'textDocument/rename': result = self.handle_rename(msg)
                elif method == 'textDocument/prepareRename': result = self.handle_prepare_rename(msg)
                elif method == 'textDocument/documentSymbol': result = self.handle_document_symbols(msg)
                elif method == 'workspace/symbol': result = self.handle_workspace_symbols(msg)
                elif method == 'textDocument/codeAction': result = self.handle_code_action(msg)
                elif method == 'textDocument/codeLens': result = self.handle_code_lens(msg)
                elif method == 'shutdown': result = None
                elif method == 'exit': break
                if 'id' in msg: self.send({'id': msg['id'], 'result': result})
            except Exception as e:
                if 'id' in msg: self.send({'id': msg['id'], 'error': {'code': -32603, 'message': str(e)}})

if __name__ == '__main__':
    AdoLSP().run()
