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
            content_length = 0
            while True:
                line = sys.stdin.readline()
                if not line: return None
                line = line.strip()
                if not line: break
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
            if content_length > 0:
                content = sys.stdin.read(content_length)
                return json.loads(content)
        except Exception:
            return None
        return None

    def send(self, msg: dict):
        content = json.dumps(msg)
        sys.stdout.write(f"Content-Length: {len(content)}\r\n\r\n{content}")
        sys.stdout.flush()

    def get_word_at_position(self, uri: str, line: int, char: int) -> str:
        text = self.docs.get(uri, "")
        lines = text.split("\n")
        if line >= len(lines): return ""
        current_line = lines[line]
        if char > len(current_line): char = len(current_line)
        start = char
        while start > 0 and re.match(r'\w', current_line[start-1]): start -= 1
        end = char
        while end < len(current_line) and re.match(r'\w', current_line[end]): end += 1
        return current_line[start:end]

    def find_symbol_occurrences(self, word: str) -> Dict[str, List[dict]]:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b')
        occurrences = {}
        for doc_uri, text in self.docs.items():
            ranges = []
            for i, doc_line in enumerate(text.split('\n')):
                comment_idx = doc_line.find('#')
                for match in pattern.finditer(doc_line):
                    if comment_idx != -1 and match.start() >= comment_idx:
                        continue

                    quotes_before = doc_line[:match.start()].count('"')
                    if quotes_before % 2 == 1:
                        continue

                    ranges.append({
                        'start': {'line': i, 'character': match.start()},
                        'end': {'line': i, 'character': match.end()}
                    })
            if ranges: occurrences[doc_uri] = ranges
        return occurrences

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




    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})

    def handle_completion(self, msg: dict) -> dict:
        items = []
        for kw in self.keywords:
            items.append({'label': kw, 'kind': 14, 'detail': 'keyword'})
        for builtin in self.builtins:
            items.append({'label': builtin, 'kind': 3, 'detail': 'builtin function'})

        seen_symbols = set(self.keywords + self.builtins)
        for sym_name, sym_list in self.symbols.items():
            if not sym_list or sym_name in seen_symbols: continue
            sym = sym_list[0]
            seen_symbols.add(sym_name)
            if sym.kind == 'function':
                params_str = ", ".join([f"${{{i+1}:{p}}}" for i, p in enumerate(sym.params)])
                items.append({
                    'label': sym.name,
                    'kind': 3,
                    'detail': f"fn {sym.name}({', '.join(sym.params)})",
                    'insertText': f"{sym.name}({params_str})",
                    'insertTextFormat': 2,
                    'documentation': sym.docstring
                })
            elif sym.kind == 'variable':
                items.append({'label': sym.name, 'kind': 6, 'detail': 'variable'})
            elif sym.kind == 'parameter':
                items.append({'label': sym.name, 'kind': 6, 'detail': 'parameter'})

        return {'isIncomplete': False, 'items': items}

    def handle_definition(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self.get_word_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        sym_list = self.symbols[word]
        if not sym_list: return None

        # Prioritize symbols in the same file
        sym = next((s for s in sym_list if s.uri == uri), sym_list[0])
        return {
            'uri': sym.uri,
            'range': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.end_line, 'character': sym.end_col}
            }
        }

    def handle_references(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self.get_word_at_position(uri, line, char)
        if not word: return []

        refs = []
        occurrences = self.find_symbol_occurrences(word)
        for doc_uri, ranges in occurrences.items():
            for r in ranges:
                refs.append({'uri': doc_uri, 'range': r})
        return refs

    def handle_hover(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self.get_word_at_position(uri, line, char)
        if not word or word not in self.symbols: return None

        sym_list = self.symbols[word]
        if not sym_list: return None
        sym = sym_list[0]

        hover_text = ""
        if sym.kind == 'function':
            hover_text = f"```ado\nfn {sym.name}({', '.join(sym.params)})\n```"
            if sym.docstring: hover_text += f"\n\n{sym.docstring}"
        elif sym.kind == 'variable':
            hover_text = f"```ado\nlet {sym.name}\n```\nVariable"
        elif sym.kind == 'parameter':
            hover_text = f"```ado\n{sym.name}\n```\nParameter"

        return {'contents': {'kind': 'markdown', 'value': hover_text}} if hover_text else None

    def handle_signature_help(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        text = self.docs.get(uri, "")
        lines = text.split("\n")
        if line >= len(lines): return None

        # Simple backwards search for function call name
        current_line = lines[line][:char]
        open_paren_idx = current_line.rfind('(')
        if open_paren_idx == -1: return None

        func_name = ""
        idx = open_paren_idx - 1
        while idx >= 0 and current_line[idx].isspace(): idx -= 1
        end_idx = idx + 1
        while idx >= 0 and re.match(r'\w', current_line[idx]): idx -= 1
        func_name = current_line[idx+1:end_idx]

        if not func_name or func_name not in self.symbols: return None

        sym_list = [s for s in self.symbols[func_name] if s.kind == 'function']
        if not sym_list: return None
        sym = sym_list[0]

        active_parameter = current_line[open_paren_idx:].count(',')

        return {
            'signatures': [{
                'label': f"{sym.name}({', '.join(sym.params)})",
                'documentation': sym.docstring,
                'parameters': [{'label': p} for p in sym.params]
            }],
            'activeSignature': 0,
            'activeParameter': active_parameter
        }

    def handle_formatting(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        options = params.get('options', {})
        tab_size = options.get('tabSize', 2)
        insert_spaces = options.get('insertSpaces', True)
        indent_char = ' ' * tab_size if insert_spaces else '\t'

        text = self.docs.get(uri, "")
        lines = text.split('\n')

        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)

            formatted_line = indent_char * indent_level + stripped

            # Simple spacing around common operators if they don't have it
            formatted_line = re.sub(r'([^<>=!])=([^=])', r'\1 = \2', formatted_line)
            formatted_line = re.sub(r'\s*,\s*', ', ', formatted_line)
            formatted_line = re.sub(r'\s*{\s*$', ' {', formatted_line)

            # Clean up potential double spaces from naive regex replacements
            formatted_line = formatted_line.replace('  =', ' =').replace('=  ', '= ')

            formatted_lines.append(formatted_line)

            if stripped.endswith('{'):
                indent_level += 1

        return [{
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': len(lines), 'character': 0}
            },
            'newText': '\n'.join(formatted_lines)
        }]

    def handle_prepare_rename(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self.get_word_at_position(uri, line, char)
        if not word or word in self.keywords or word in self.builtins: return None

        # Verify it's a valid symbol
        if word not in self.symbols: return None

        # Return a range to highlight in the editor
        # Simplification: just return a range spanning the found word at the cursor
        return {
            'start': {'line': line, 'character': char - len(word)},
            'end': {'line': line, 'character': char}
        }

    def handle_rename(self, msg: dict) -> Optional[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')
        pos = params.get('position', {})
        new_name = params.get('newName', '')
        line, char = pos.get('line', 0), pos.get('character', 0)

        word = self.get_word_at_position(uri, line, char)
        if not word or word in self.keywords or word in self.builtins: return None
        if word not in self.symbols: return None

        changes = {}
        occurrences = self.find_symbol_occurrences(word)
        for doc_uri, ranges in occurrences.items():
            changes[doc_uri] = [{'range': r, 'newText': new_name} for r in ranges]

        return {'changes': changes} if changes else None

    def handle_document_symbols(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')

        doc_symbols = []
        for sym_list in self.symbols.values():
            for sym in sym_list:
                if sym.uri == uri:
                    kind_map = {'function': 12, 'variable': 13, 'parameter': 13}
                    doc_symbols.append({
                        'name': sym.name,
                        'kind': kind_map.get(sym.kind, 1),
                        'location': {
                            'uri': uri,
                            'range': {
                                'start': {'line': sym.line, 'character': sym.col},
                                'end': {'line': sym.end_line, 'character': sym.end_col}
                            }
                        }
                    })
        return doc_symbols

    def handle_workspace_symbols(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        query = params.get('query', '').lower()

        workspace_symbols = []
        for name, sym_list in self.symbols.items():
            if query and query not in name.lower(): continue
            for sym in sym_list:
                kind_map = {'function': 12, 'variable': 13, 'parameter': 13}
                workspace_symbols.append({
                    'name': sym.name,
                    'kind': kind_map.get(sym.kind, 1),
                    'location': {
                        'uri': sym.uri,
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}
                        }
                    }
                })
        return workspace_symbols

    def handle_code_action(self, msg: dict) -> List[dict]:
        # Minimal code action implementation
        # Could provide actions for known diagnostic errors here
        return []

    def handle_code_lens(self, msg: dict) -> List[dict]:
        params = msg.get('params', {})
        uri = params.get('textDocument', {}).get('uri', '')

        lenses = []
        for sym_list in self.symbols.values():
            for sym in sym_list:
                if sym.uri == uri and sym.kind == 'function':
                    # Count references (simplified)
                    refs = 0
                    occurrences = self.find_symbol_occurrences(sym.name)
                    for ranges in occurrences.values():
                        refs += len(ranges)

                    # Subtract definition
                    refs = max(0, refs - 1)

                    lenses.append({
                        'range': {
                            'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}
                        },
                        'command': {
                            'title': f"{refs} references",
                            'command': ""
                        }
                    })
        return lenses

    def handle_initialize(self, msg: dict) -> dict:
        return {
            'capabilities': {
                'textDocumentSync': 1,
                'completionProvider': {'resolveProvider': False, 'triggerCharacters': ['.']},
                'definitionProvider': True,
                'referencesProvider': True,
                'hoverProvider': True,
                'signatureHelpProvider': {'triggerCharacters': ['(']},
                'documentFormattingProvider': True,
                'renameProvider': {'prepareProvider': True},
                'documentSymbolProvider': True,
                'workspaceSymbolProvider': True,
                'codeActionProvider': True,
                'codeLensProvider': {'resolveProvider': False}
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
