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




    def send(self, msg: dict):
        body = json.dumps(msg, separators=(',', ':')).encode('utf-8')
        sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode('utf-8'))
        sys.stdout.buffer.write(body)
        sys.stdout.buffer.flush()

    def recv(self) -> Optional[dict]:
        try:
            line = sys.stdin.buffer.readline().decode('utf-8')
            if not line:
                return None
            while not line.startswith("Content-Length:"):
                line = sys.stdin.buffer.readline().decode('utf-8')
                if not line:
                    return None
            content_length = int(line.split(":")[1].strip())
            while line != "\r\n" and line != "\n":
                line = sys.stdin.buffer.readline().decode('utf-8')
                if not line:
                    return None
            body = sys.stdin.buffer.read(content_length).decode('utf-8')
            return json.loads(body)
        except Exception:
            return None

    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})

    def handle_completion(self, msg: dict) -> dict:
        items = []
        for kw in self.keywords:
            items.append({'label': kw, 'kind': 14}) # Keyword
        for sym_name, sym_list in self.symbols.items():
            if not sym_list: continue
            sym = sym_list[-1]
            kind = 3 if sym.kind == 'function' else 6 # Function or Variable
            items.append({'label': sym.name, 'kind': kind, 'detail': sym.kind})
        return {'isIncomplete': False, 'items': items}

    def _get_symbol_at_position(self, uri: str, line: int, char: int) -> Optional[str]:
        text = self.docs.get(uri, "")
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        # simple word extraction around cursor
        start = char
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'):
            start -= 1
        end = char
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'):
            end += 1

        word = ltext[start:end]
        return word if word else None

    def handle_definition(self, msg: dict) -> Optional[List[dict]]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self._get_symbol_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        syms = self.symbols[word]
        if not syms: return None
        sym = syms[-1] # go to the latest definition

        return [{
            'uri': sym.uri,
            'range': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.end_line, 'character': sym.end_col}
            }
        }]

    def handle_references(self, msg: dict) -> Optional[List[dict]]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self._get_symbol_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        res = []
        for sym in self.symbols[word]:
            res.append({
                'uri': sym.uri,
                'range': {
                    'start': {'line': sym.line, 'character': sym.col},
                    'end': {'line': sym.end_line, 'character': sym.end_col}
                }
            })
        return res

    def handle_hover(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self._get_symbol_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        sym = self.symbols[word][-1]
        hover_text = f"**{sym.name}** ({sym.kind})"
        if sym.kind == 'function':
            hover_text += f"\n\n`fn {sym.name}({', '.join(sym.params)})`"
        if sym.docstring:
            hover_text += f"\n\n{sym.docstring}"

        return {
            'contents': {
                'kind': 'markdown',
                'value': hover_text
            }
        }

    def handle_signature_help(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        text = self.docs.get(uri, "")
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line][:char]

        # Simple heuristic: find last unclosed '('
        paren_idx = ltext.rfind('(')
        if paren_idx == -1: return None

        # Count commas to find active parameter
        active_param = ltext[paren_idx+1:].count(',')

        word = self._get_symbol_at_position(uri, line, paren_idx)
        if not word or word not in self.symbols: return None

        sym = self.symbols[word][-1]
        if sym.kind != 'function': return None

        sig_label = f"{sym.name}({', '.join(sym.params)})"
        parameters = [{'label': p} for p in sym.params]

        return {
            'signatures': [{
                'label': sig_label,
                'parameters': parameters
            }],
            'activeSignature': 0,
            'activeParameter': active_param
        }

    def handle_prepare_rename(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self._get_symbol_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        text = self.docs.get(uri, "")
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        start = char
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'):
            start -= 1
        end = char
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'):
            end += 1

        return {
            'range': {
                'start': {'line': line, 'character': start},
                'end': {'line': line, 'character': end}
            },
            'placeholder': word
        }

    def handle_rename(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)
        new_name = params.get('newName', '')

        word = self._get_symbol_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        changes = {}
        for sym in self.symbols[word]:
            if sym.uri not in changes: changes[sym.uri] = []
            changes[sym.uri].append({
                'range': {
                    'start': {'line': sym.line, 'character': sym.col},
                    'end': {'line': sym.line, 'character': sym.col + len(word)}
                },
                'newText': new_name
            })

        return {'changes': changes}

    def handle_document_symbols(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')

        symbols = []
        for sym_list in self.symbols.values():
            for sym in sym_list:
                if sym.uri == uri:
                    kind = 12 if sym.kind == 'function' else 13 # Function or Variable DocumentSymbol kind
                    symbols.append({
                        'name': sym.name,
                        'kind': kind,
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}
                        },
                        'selectionRange': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.line, 'character': sym.col + len(sym.name)}
                        }
                    })
        return symbols

    def handle_workspace_symbols(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        query = params.get('query', '').lower()

        symbols = []
        for sym_name, sym_list in self.symbols.items():
            if query and query not in sym_name.lower(): continue
            for sym in sym_list:
                kind = 12 if sym.kind == 'function' else 13
                symbols.append({
                    'name': sym.name,
                    'kind': kind,
                    'location': {
                        'uri': sym.uri,
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}
                        }
                    }
                })
        return symbols

    def handle_formatting(self, msg: dict) -> List[dict]:
        # Return empty list, meaning no edits (pass-through for now)
        return []

    def handle_code_action(self, msg: dict) -> List[dict]:
        return []

    def handle_code_lens(self, msg: dict) -> List[dict]:
        return []

    def handle_initialize(self, msg: dict) -> dict:
        return {
            'capabilities': {
                'textDocumentSync': 1,
                'completionProvider': {
                    'resolveProvider': False,
                    'triggerCharacters': ['.']
                },
                'definitionProvider': True,
                'typeDefinitionProvider': True,
                'referencesProvider': True,
                'hoverProvider': True,
                'signatureHelpProvider': {
                    'triggerCharacters': ['(']
                },
                'renameProvider': {
                    'prepareProvider': True
                },
                'documentFormattingProvider': True,
                'documentRangeFormattingProvider': True,
                'documentSymbolProvider': True,
                'workspaceSymbolProvider': True,
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
