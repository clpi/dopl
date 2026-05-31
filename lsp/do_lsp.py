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

    def recv(self) -> Optional[dict]:
        try:
            line = sys.stdin.buffer.readline()
            if not line:
                return None
            line = line.decode('utf-8')

            while line and not line.startswith("Content-Length: "):
                line = sys.stdin.buffer.readline().decode('utf-8')

            if not line.startswith("Content-Length: "):
                return None

            length = int(line[16:].strip())

            while True:
                line = sys.stdin.buffer.readline().decode('utf-8')
                if not line.strip():
                    break

            content = sys.stdin.buffer.read(length).decode('utf-8')
            return json.loads(content)
        except Exception:
            return None

    def send(self, msg: dict):
        try:
            content = json.dumps(msg, separators=(',', ':')).encode('utf-8')
            sys.stdout.buffer.write(f"Content-Length: {len(content)}\r\n\r\n".encode('utf-8'))
            sys.stdout.buffer.write(content)
            sys.stdout.buffer.flush()
        except Exception:
            pass

    def parse_symbols(self, uri: str, text: str):
        symbols = []
        lines = text.split('\n')
        fn_pattern = re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)')
        let_pattern = re.compile(r'let\s+(\w+)\s*=')

        brace_count = 0
        active_functions = []

        for i, raw_line in enumerate(lines):
            # Remove string literals and comments for symbol parsing
            line = re.sub(r'"([^"\\]|\\.)*"', '""', raw_line)
            if '#' in line:
                line = line[:line.index('#')]

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

        for i, raw_line in enumerate(lines):
            line = re.sub(r'"([^"\\]|\\.)*"', '""', raw_line)
            if '#' in line:
                line = line[:line.index('#')]

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
        for i, raw_line in enumerate(lines):
            line = re.sub(r'"([^"\\]|\\.)*"', '""', raw_line)
            if '#' in line:
                line = line[:line.index('#')]

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




    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})

    def handle_initialize(self, msg: dict) -> dict:
        return {
            'capabilities': {
                'textDocumentSync': 1,  # Full sync
                'completionProvider': {
                    'resolveProvider': False,
                    'triggerCharacters': ['.']
                },
                'definitionProvider': True,
                'typeDefinitionProvider': True,
                'referencesProvider': True,
                'hoverProvider': True,
                'signatureHelpProvider': {
                    'triggerCharacters': ['(', ',']
                },
                'documentFormattingProvider': True,
                'documentRangeFormattingProvider': True,
                'renameProvider': {
                    'prepareProvider': True
                },
                'documentSymbolProvider': True,
                'workspaceSymbolProvider': True,
                'codeActionProvider': True,
                'codeLensProvider': {
                    'resolveProvider': False
                }
            }
        }

    def handle_completion(self, msg: dict) -> list:
        # Provide basic completion using keywords and symbols
        items = []
        for kw in self.keywords:
            items.append({
                'label': kw,
                'kind': 14, # Keyword
            })
        for kw in self.builtins:
            items.append({
                'label': kw,
                'kind': 3, # Function
            })
        for name, syms in self.symbols.items():
            if not syms: continue
            sym = syms[-1]
            kind = 6 # Variable
            if sym.kind == 'function': kind = 3 # Function
            if sym.kind == 'parameter': kind = 6
            items.append({
                'label': name,
                'kind': kind,
                'detail': f"Ado {sym.kind}"
            })
        # Basic snippet support for function definition and loops
        items.append({'label': 'fn', 'kind': 15, 'insertText': 'fn ${1:name}(${2:params}) {\n  $0\n}', 'insertTextFormat': 2})
        items.append({'label': 'if', 'kind': 15, 'insertText': 'if ${1:condition} {\n  $0\n}', 'insertTextFormat': 2})
        items.append({'label': 'while', 'kind': 15, 'insertText': 'while ${1:condition} {\n  $0\n}', 'insertTextFormat': 2})
        items.append({'label': 'for', 'kind': 15, 'insertText': 'for ${1:i} in ${2:0} .. ${3:10} {\n  $0\n}', 'insertTextFormat': 2})

        return items

    def handle_definition(self, msg: dict) -> list:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return []
        ltext = lines[line]

        # Find the word under the cursor
        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1
        word = ltext[start:end]

        if word in self.symbols:
            locs = []
            for sym in self.symbols[word]:
                locs.append({
                    'uri': sym.uri,
                    'range': {
                        'start': {'line': sym.line, 'character': sym.col},
                        'end': {'line': sym.end_line, 'character': sym.end_col}
                    }
                })
            return locs
        return []

    def handle_references(self, msg: dict) -> list:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return []
        ltext = lines[line]

        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1
        word = ltext[start:end]

        refs = []
        if word and word not in self.keywords and word not in self.builtins:
            for doc_uri, doc_text in self.docs.items():
                doc_lines = doc_text.split('\n')
                for i, doc_line in enumerate(doc_lines):
                    # basic string/comment exclusion is ideal but we can do a simple regex finditer here
                    for match in re.finditer(r'\b' + re.escape(word) + r'\b', doc_line):
                        refs.append({
                            'uri': doc_uri,
                            'range': {
                                'start': {'line': i, 'character': match.start()},
                                'end': {'line': i, 'character': match.end()}
                            }
                        })
        return refs

    def handle_hover(self, msg: dict) -> dict:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1
        word = ltext[start:end]

        if word in self.symbols and self.symbols[word]:
            sym = self.symbols[word][-1]
            if sym.kind == 'function':
                params_str = ", ".join(sym.params)
                val = f"```ado\nfn {sym.name}({params_str})\n```"
                if sym.docstring: val += f"\n---\n{sym.docstring}"
                return {'contents': {'kind': 'markdown', 'value': val}}
            elif sym.kind == 'variable':
                return {'contents': {'kind': 'markdown', 'value': f"```ado\nlet {sym.name}\n```"}}
            elif sym.kind == 'parameter':
                return {'contents': {'kind': 'markdown', 'value': f"```ado\n(parameter) {sym.name}\n```"}}
        elif word in self.builtins:
            val = f"```ado\n{word}(...)\n```\n---\nBuilt-in Ado function."
            return {'contents': {'kind': 'markdown', 'value': val}}
        return None

    def handle_signature_help(self, msg: dict) -> dict:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        # Find the function name by walking backwards from parenthesis
        idx = col - 1
        while idx >= 0 and ltext[idx] != '(':
            idx -= 1
        if idx < 0: return None

        start = idx - 1
        while start >= 0 and ltext[start].isspace(): start -= 1
        end = start + 1
        while start >= 0 and (ltext[start].isalnum() or ltext[start] == '_'): start -= 1
        start += 1

        word = ltext[start:end]
        if word in self.symbols and self.symbols[word] and self.symbols[word][-1].kind == 'function':
            sym = self.symbols[word][-1]
            params_str = ", ".join(sym.params)
            sig_label = f"{sym.name}({params_str})"
            param_infos = [{'label': p} for p in sym.params]

            # Count commas to find active parameter
            active_param = 0
            for i in range(idx + 1, col):
                if ltext[i] == ',': active_param += 1

            return {
                'signatures': [{
                    'label': sig_label,
                    'parameters': param_infos,
                    'documentation': sym.docstring
                }],
                'activeSignature': 0,
                'activeParameter': active_param
            }
        return None

    def handle_formatting(self, msg: dict) -> list:
        params = msg['params']
        uri = params['textDocument']['uri']
        text = self.docs.get(uri, '')
        lines = text.split('\n')

        formatted = []
        indent = 0
        for line in lines:
            sline = line.strip()
            if sline == '':
                formatted.append('')
                continue

            if sline.startswith('}'):
                indent = max(0, indent - 1)

            formatted.append(('  ' * indent) + sline)

            if sline.endswith('{'):
                indent += 1

        new_text = '\n'.join(formatted)

        if text != new_text:
            return [{
                'range': {
                    'start': {'line': 0, 'character': 0},
                    'end': {'line': len(lines), 'character': 0}
                },
                'newText': new_text
            }]
        return []

    def handle_prepare_rename(self, msg: dict) -> dict:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1
        word = ltext[start:end]

        if word and word not in self.keywords and word not in self.builtins:
            return {
                'range': {
                    'start': {'line': line, 'character': start},
                    'end': {'line': line, 'character': end}
                },
                'placeholder': word
            }
        return None

    def handle_rename(self, msg: dict) -> dict:
        params = msg['params']
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        col = pos['character']
        new_name = params['newName']

        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return None
        ltext = lines[line]

        start = col
        while start > 0 and (ltext[start-1].isalnum() or ltext[start-1] == '_'): start -= 1
        end = col
        while end < len(ltext) and (ltext[end].isalnum() or ltext[end] == '_'): end += 1
        word = ltext[start:end]

        if not word or word in self.keywords or word in self.builtins:
            return None

        changes = {}
        for doc_uri, doc_text in self.docs.items():
            edits = []
            doc_lines = doc_text.split('\n')
            for i, doc_line in enumerate(doc_lines):
                for match in re.finditer(r'\b' + re.escape(word) + r'\b', doc_line):
                    edits.append({
                        'range': {
                            'start': {'line': i, 'character': match.start()},
                            'end': {'line': i, 'character': match.end()}
                        },
                        'newText': new_name
                    })
            if edits:
                changes[doc_uri] = edits

        return {'changes': changes}

    def handle_document_symbols(self, msg: dict) -> list:
        params = msg['params']
        uri = params['textDocument']['uri']

        doc_syms = []
        for name, syms in self.symbols.items():
            for sym in syms:
                if sym.uri == uri and sym.kind in ('function', 'variable'):
                    kind = 12 if sym.kind == 'function' else 13
                    doc_syms.append({
                        'name': name,
                        'kind': kind,
                        'location': {
                            'uri': uri,
                            'range': {
                                'start': {'line': sym.line, 'character': sym.col},
                                'end': {'line': sym.end_line, 'character': sym.end_col}
                            }
                        }
                    })
        return doc_syms

    def handle_workspace_symbols(self, msg: dict) -> list:
        query = msg['params'].get('query', '').lower()

        syms_out = []
        for name, syms in self.symbols.items():
            if query and query not in name.lower(): continue
            for sym in syms:
                if sym.kind in ('function', 'variable'):
                    kind = 12 if sym.kind == 'function' else 13
                    syms_out.append({
                        'name': name,
                        'kind': kind,
                        'location': {
                            'uri': sym.uri,
                            'range': {
                                'start': {'line': sym.line, 'character': sym.col},
                                'end': {'line': sym.end_line, 'character': sym.end_col}
                            }
                        }
                    })
        return syms_out

    def handle_code_action(self, msg: dict) -> list:
        # Provide basic code actions (e.g. for diagnostics)
        params = msg['params']
        uri = params['textDocument']['uri']
        context = params.get('context', {})
        diagnostics = context.get('diagnostics', [])

        actions = []
        for diag in diagnostics:
            if "brace" in diag.get('message', '').lower():
                actions.append({
                    'title': "Format document to check braces",
                    'kind': 'quickfix',
                    'command': {
                        'title': "Format",
                        'command': "editor.action.formatDocument"
                    }
                })
        return actions

    def handle_code_lens(self, msg: dict) -> list:
        params = msg['params']
        uri = params['textDocument']['uri']

        lenses = []
        for name, syms in self.symbols.items():
            for sym in syms:
                if sym.uri == uri and sym.kind == 'function':
                    # Count references
                    ref_count = 0
                    for doc_text in self.docs.values():
                        for doc_line in doc_text.split('\n'):
                            ref_count += len(re.findall(r'\b' + re.escape(name) + r'\b', doc_line))

                    # Subtract definition
                    ref_count = max(0, ref_count - 1)

                    lenses.append({
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.line, 'character': sym.col + len(name)}
                        },
                        'command': {
                            'title': f"{ref_count} reference{'s' if ref_count != 1 else ''}",
                            'command': ""
                        }
                    })
        return lenses

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
