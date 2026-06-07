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
    scope_start_line: int = 0
    scope_start_col: int = 0
    scope_end_line: int = 999999
    scope_end_col: int = 999999

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
        self.keywords = ['fn', 'let', 'if', 'else', 'while', 'for', 'return', 'in',
                         'true', 'false', 'and', 'or', 'not', 'print', 'len', 'push',
                         'hint', 'type', 'inline', 'const', 'static']
        self.builtins = ['print', 'len', 'push', 'abs', 'min', 'max', 'pow', 'clamp', 'sign', 'is_even', 'is_odd', 'gcd', 'lcm', 'factorial', 'fib', 'sum', 'avg', 'take', 'drop', 'concat', 'fill', 'slice']

    def _mask_text(self, text: str) -> str:
        """Replace contents of string literals and comments with spaces to avoid false positives."""
        masked = list(text)
        in_string = False
        in_comment = False
        for i, char in enumerate(masked):
            if in_comment:
                if char == '\n':
                    in_comment = False
                else:
                    masked[i] = ' '
            elif in_string:
                if char == '"':
                    in_string = False
                else:
                    masked[i] = ' '
            else:
                if char == '"':
                    in_string = True
                elif char == '#':
                    in_comment = True
        return "".join(masked)

    def parse_symbols(self, uri: str, text: str):
        masked_text = self._mask_text(text)
        symbols = []
        lines = text.split('\n')
        masked_lines = masked_text.split('\n')
        fn_pattern = re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)')
        let_pattern = re.compile(r'let\s+(\w+)\s*=')

        brace_count = 0
        active_functions = []
        active_scopes = []
        active_variables = []
        active_parameters = []

        for i, (line, masked_line) in enumerate(zip(lines, masked_lines)):
            match = fn_pattern.search(masked_line)
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

                # Parameters scope is the function body
                for param in params:
                    param_pattern = re.compile(r'\b' + re.escape(param) + r'\b')
                    param_match = param_pattern.search(masked_line)
                    if param_match:
                        p_sym = Symbol(name=param, kind='parameter', uri=uri,
                            line=i, col=param_match.start(), end_line=i, end_col=param_match.end(),
                            scope_start_line=i, scope_start_col=param_match.end())
                        symbols.append(p_sym)
                        active_parameters.append({
                            'symbol': p_sym,
                            'func_base_count': brace_count,
                            'started': False
                        })

            for idx, char in enumerate(masked_line):
                if char == '{':
                    for func_data in active_functions:
                        if not func_data['started']:
                            func_data['started'] = True
                            func_data['base_count'] = brace_count
                    for p_data in active_parameters:
                        if not p_data['started'] and p_data['func_base_count'] == brace_count:
                            p_data['started'] = True
                            p_data['func_base_count'] = brace_count

                    brace_count += 1
                    active_scopes.append({'brace_count': brace_count, 'line': i, 'col': idx})
                elif char == '}':
                    if active_functions:
                        remaining_functions = []
                        for func_data in active_functions:
                            if func_data['started'] and brace_count == func_data['base_count'] + 1:
                                func_data['symbol'].end_line = i
                                func_data['symbol'].end_col = idx + 1
                            else:
                                remaining_functions.append(func_data)
                        active_functions = remaining_functions

                    if active_parameters:
                        remaining_parameters = []
                        for p_data in active_parameters:
                            if p_data['started'] and brace_count == p_data['func_base_count'] + 1:
                                p_data['symbol'].scope_end_line = i
                                p_data['symbol'].scope_end_col = idx
                            else:
                                remaining_parameters.append(p_data)
                        active_parameters = remaining_parameters

                    if active_variables:
                        remaining_variables = []
                        for v_data in active_variables:
                            if v_data['brace_count'] == brace_count:
                                v_data['symbol'].scope_end_line = i
                                v_data['symbol'].scope_end_col = idx
                            else:
                                remaining_variables.append(v_data)
                        active_variables = remaining_variables

                    if active_scopes:
                        active_scopes.pop()
                    brace_count -= 1

            # Variables
            for match in let_pattern.finditer(masked_line):
                v_sym = Symbol(name=match.group(1), kind='variable', uri=uri,
                    line=i, col=match.start(1), end_line=i, end_col=match.end(1),
                    scope_start_line=i, scope_start_col=match.end(1))
                symbols.append(v_sym)
                active_variables.append({
                    'symbol': v_sym,
                    'brace_count': brace_count
                })

            # Destructuring: let [a, b, ...rest] = arr
            destruct_pattern = re.compile(r'let\s*\[\s*([^]]*)\]')
            destruct_match = destruct_pattern.search(masked_line)
            if destruct_match:
                names_str = destruct_match.group(1)
                # Parse names and ...rest
                parts = [p.strip() for p in names_str.split(',')]
                for part in parts:
                    if '...' in part:
                        # ...rest pattern
                        rest_name = part.replace('...', '').strip()
                        if rest_name:
                            d_sym = Symbol(name=rest_name, kind='variable', uri=uri,
                                line=i, col=destruct_match.start() + 5 + names_str.find(rest_name), 
                                end_line=i, end_col=destruct_match.start() + 5 + names_str.find(rest_name) + len(rest_name),
                                scope_start_line=i, scope_start_col=destruct_match.end() + 1)
                            symbols.append(d_sym)
                    elif part:
                        # Regular name
                        d_sym = Symbol(name=part, kind='variable', uri=uri,
                            line=i, col=destruct_match.start() + 5 + names_str.find(part),
                            end_line=i, end_col=destruct_match.start() + 5 + names_str.find(part) + len(part),
                            scope_start_line=i, scope_start_col=destruct_match.end() + 1)
                        symbols.append(d_sym)

        for sym in symbols:
            if sym.name not in self.symbols: self.symbols[sym.name] = []
            self.symbols[sym.name] = [s for s in self.symbols[sym.name] if s.uri != uri]
            self.symbols[sym.name].append(sym)
    def get_diagnostics(self, uri: str, text: str) -> List[dict]:
        diagnostics = []
        masked_text = self._mask_text(text)
        # First check for unbalanced braces just in case
        lines = masked_text.split('\n')
        brace_stack = []
        paren_stack = []

        let_pattern = re.compile(r'\blet\s+(\w+)\s*(?:[^=]*)$')
        call_pattern = re.compile(r'\b(\w+)\s*\(')
        word_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')

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

            # Check for missing let assignments
            match = re.search(r'\blet\s+(\w+)(?![^=]*=)', line)
            if match:
                diagnostics.append({
                    'range': {
                        'start': {'line': i, 'character': match.start(1)},
                        'end': {'line': i, 'character': match.end(1)}
                    },
                    'severity': 1,
                    'message': 'let statement requires assignment',
                    'source': 'ado-lsp'
                })

            # Check for undefined functions
            for match in call_pattern.finditer(line):
                func_name = match.group(1)
                if func_name not in self.symbols and func_name not in self.keywords and func_name not in self.builtins:
                    diagnostics.append({
                        'range': {
                            'start': {'line': i, 'character': match.start(1)},
                            'end': {'line': i, 'character': match.end(1)}
                        },
                        'severity': 2, # Warning
                        'message': f'Undefined function: {func_name}',
                        'source': 'ado-lsp'
                    })

            # Check for undefined variables
            # We don't want to flag function names, keywords, or the variable part of `let x`
            masked_line = masked_text.split('\n')[i]
            for match in word_pattern.finditer(masked_line):
                word = match.group(0)
                if word in self.keywords or word in self.builtins:
                    continue

                # If it's part of a function definition `fn x` or `let x`, ignore
                prev_word_match = re.search(r'\b(fn|let)\s+$', line[:match.start()])
                if prev_word_match:
                    continue

                # Ignore function parameters during their definition
                # We can check if it's within a function parameter list
                is_param_def = False
                for sym_list in self.symbols.values():
                    for s in sym_list:
                        if s.kind == 'parameter' and s.line == i and s.col == match.start():
                            is_param_def = True
                            break
                    if is_param_def:
                        break
                if is_param_def:
                    continue

                # If it's a function call, handled above
                if match.end() < len(line) and line[match.end():].lstrip().startswith('('):
                    continue

                # Check if it resolves
                sym = self.resolve_symbol(uri, word, i, match.start())
                if not sym:
                    diagnostics.append({
                        'range': {
                            'start': {'line': i, 'character': match.start()},
                            'end': {'line': i, 'character': match.end()}
                        },
                        'severity': 2, # Warning
                        'message': f'Undefined variable: {word}',
                        'source': 'ado-lsp'
                    })

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
            content_bytes = content.encode('utf-8')
            sys.stdout.write(f"Content-Length: {len(content_bytes)}\r\n\r\n{content}")
            sys.stdout.flush()
            sys.stdout.flush()
        except Exception:
            pass

    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})


    def resolve_symbol(self, uri: str, name: str, line: int, col: int) -> Optional[Symbol]:
        if name not in self.symbols:
            return None

        best_sym = None
        for sym in self.symbols[name]:
            if sym.uri != uri and sym.kind != 'function':
                continue

            if sym.kind == 'function':
                if not best_sym:
                    best_sym = sym
                continue

            # Check if in scope
            in_scope = False
            # Allow resolving the symbol if we're hovering/querying exactly on its definition
            if sym.line == line and sym.col <= col <= sym.end_col:
                in_scope = True
            elif sym.scope_start_line < line < sym.scope_end_line:
                in_scope = True
            elif sym.scope_start_line == line and sym.scope_end_line == line:
                if sym.scope_start_col <= col <= sym.scope_end_col:
                    in_scope = True
            elif sym.scope_start_line == line:
                if col >= sym.scope_start_col:
                    in_scope = True
            elif sym.scope_end_line == line:
                if col <= sym.scope_end_col:
                    in_scope = True

            if in_scope:
                if best_sym is None or best_sym.kind == 'function':
                    best_sym = sym
                else:
                    if sym.scope_start_line > best_sym.scope_start_line or (sym.scope_start_line == best_sym.scope_start_line and sym.scope_start_col > best_sym.scope_start_col):
                        best_sym = sym

        return best_sym

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
        if not word:
            return []

        sym = self.resolve_symbol(uri, word, line, col)
        if not sym:
            return []

        return [{
            'uri': sym.uri,
            'range': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.end_line, 'character': sym.end_col}
            }
        }]

    def find_references(self, word: str, restrict_uri: Optional[str] = None, restrict_sym: Optional[Symbol] = None) -> List[dict]:
        refs = []
        pattern = re.compile(r'\b' + re.escape(word) + r'\b')
        docs_to_search = {restrict_uri: self.docs[restrict_uri]} if restrict_uri and restrict_uri in self.docs else self.docs

        for doc_uri, text in docs_to_search.items():
            masked_text = self._mask_text(text)
            lines = masked_text.split('\n')
            for i, line in enumerate(lines):
                if restrict_sym and restrict_sym.kind != 'function' and restrict_uri == doc_uri:
                    if i < restrict_sym.scope_start_line or i > restrict_sym.scope_end_line:
                        continue

                for match in pattern.finditer(line):
                    if restrict_sym and restrict_sym.kind != 'function' and restrict_uri == doc_uri:
                        if i == restrict_sym.scope_start_line and match.start() < restrict_sym.scope_start_col:
                            if not (i == restrict_sym.line and match.start() == restrict_sym.col):
                                continue
                        if i == restrict_sym.scope_end_line and match.end() > restrict_sym.scope_end_col:
                            continue

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

        syms = self.symbols.get(word, [])
        is_local = any(s.kind in ('variable', 'parameter') for s in syms)
        return self.find_references(word, restrict_uri=uri if is_local else None)

    def handle_hover(self, msg: dict) -> Optional[dict]:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word:
            return None

        # Check builtins first for better hover info
        builtin_docs = {
            'print': 'print(values...) - Print values to stdout',
            'len': 'len(arr) - Get array length',
            'push': 'push(&arr, val) - Append value to array',
            'abs': 'abs(x) - Absolute value',
            'min': 'min(a, b) - Minimum of two values',
            'max': 'max(a, b) - Maximum of two values',
            'pow': 'pow(base, exp) - Power function',
            'clamp': 'clamp(x, low, high) - Clamp value to range',
            'slice': 'arr[start..end] - Array slice (exclusive end)',
        }

        if word in builtin_docs:
            return {'contents': {'kind': 'markdown', 'value': f"```ado\n{builtin_docs[word]}\n```"}}

        if word not in self.symbols:
            return None

        sym = None
        for s in self.symbols[word]:
            if s.uri == uri and s.line <= line:
                sym = s
                break
        if not sym:
            same_file_syms = [s for s in self.symbols[word] if s.uri == uri]
            sym = same_file_syms[0] if same_file_syms else self.symbols[word][0]

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

        masked_text = self._mask_text(text)
        lines = text.split('\n')
        masked_lines = masked_text.split('\n')
        formatted_lines = []
        indent_level = 0

        for line, masked_line in zip(lines, masked_lines):
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # Check masked string for braces
            brace_check_line = masked_line.strip()

            # Decrease indent for closing brace
            if brace_check_line.startswith('}'):
                indent_level = max(0, indent_level - 1)

            formatted_lines.append("  " * indent_level + stripped)

            # Increase indent for opening brace
            if brace_check_line.endswith('{'):
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
        uri = msg['params']['textDocument']['uri']
        context = msg['params'].get('context', {})
        diagnostics = context.get('diagnostics', [])

        actions = []
        for diag in diagnostics:
            if diag.get('message') == 'let statement requires assignment':
                actions.append({
                    'title': 'Initialize variable',
                    'kind': 'quickfix',
                    'diagnostics': [diag],
                    'edit': {
                        'changes': {
                            uri: [{
                                'range': {
                                    'start': diag['range']['end'],
                                    'end': diag['range']['end']
                                },
                                'newText': ' = 0'
                            }]
                        }
                    }
                })
        return actions

    def handle_prepare_call_hierarchy(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word or word not in self.symbols: return []

        sym = self.symbols[word][0]
        if sym.kind != 'function': return []

        return [{
            'name': sym.name,
            'kind': 12, # Function
            'uri': sym.uri,
            'range': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.end_line, 'character': sym.end_col}
            },
            'selectionRange': {
                'start': {'line': sym.line, 'character': sym.col},
                'end': {'line': sym.line, 'character': sym.col + len(sym.name)}
            }
        }]

    def handle_call_hierarchy_incoming(self, msg: dict) -> list:
        item = msg['params']['item']
        func_name = item['name']

        refs = self.find_references(func_name)
        incoming = []

        for ref in refs:
            ref_uri = ref['uri']
            ref_line = ref['range']['start']['line']

            # Find which function this reference is inside
            caller_sym = None
            for name, sym_list in self.symbols.items():
                for sym in sym_list:
                    if sym.kind == 'function' and sym.uri == ref_uri:
                        if sym.line <= ref_line <= sym.end_line:
                            caller_sym = sym
                            break
                if caller_sym: break

            if caller_sym:
                incoming.append({
                    'from': {
                        'name': caller_sym.name,
                        'kind': 12, # Function
                        'uri': caller_sym.uri,
                        'range': {
                            'start': {'line': caller_sym.line, 'character': caller_sym.col},
                            'end': {'line': caller_sym.end_line, 'character': caller_sym.end_col}
                        },
                        'selectionRange': {
                            'start': {'line': caller_sym.line, 'character': caller_sym.col},
                            'end': {'line': caller_sym.line, 'character': caller_sym.col + len(caller_sym.name)}
                        }
                    },
                    'fromRanges': [ref['range']]
                })
        return incoming

    def handle_call_hierarchy_outgoing(self, msg: dict) -> list:
        item = msg['params']['item']
        uri = item['uri']

        start_line = item['range']['start']['line']
        end_line = item['range']['end']['line']

        text = self.docs.get(uri)
        if not text: return []

        masked_text = self._mask_text(text)
        lines = masked_text.split('\n')

        outgoing = []
        call_pattern = re.compile(r'\b(\w+)\s*\(')

        for i in range(start_line, min(end_line + 1, len(lines))):
            for match in call_pattern.finditer(lines[i]):
                called_name = match.group(1)
                if called_name in self.symbols and self.symbols[called_name][0].kind == 'function':
                    called_sym = self.symbols[called_name][0]
                    outgoing.append({
                        'to': {
                            'name': called_sym.name,
                            'kind': 12, # Function
                            'uri': called_sym.uri,
                            'range': {
                                'start': {'line': called_sym.line, 'character': called_sym.col},
                                'end': {'line': called_sym.end_line, 'character': called_sym.end_col}
                            },
                            'selectionRange': {
                                'start': {'line': called_sym.line, 'character': called_sym.col},
                                'end': {'line': called_sym.line, 'character': called_sym.col + len(called_sym.name)}
                            }
                        },
                        'fromRanges': [{
                            'start': {'line': i, 'character': match.start(1)},
                            'end': {'line': i, 'character': match.end(1)}
                        }]
                    })
        return outgoing

    def handle_folding_range(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri)
        if not text: return []

        masked_text = self._mask_text(text)
        lines = masked_text.split('\n')

        folds = []
        stack = []

        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char == '{':
                    stack.append((i, j))
                elif char == '}':
                    if stack:
                        start_line, start_col = stack.pop()
                        if start_line < i:
                            folds.append({
                                'startLine': start_line,
                                'startCharacter': start_col,
                                'endLine': i,
                                'endCharacter': j,
                                'kind': 'region'
                            })
        
        # Also fold multi-line comments (# ... blocks)
        in_comment_block = False
        comment_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') and not in_comment_block:
                in_comment_block = True
                comment_start = i
            elif not stripped.startswith('#') and in_comment_block and stripped:
                if i - comment_start > 1:
                    folds.append({
                        'startLine': comment_start,
                        'startCharacter': 0,
                        'endLine': i - 1,
                        'endCharacter': len(lines[i-1]),
                        'kind': 'comment'
                    })
                in_comment_block = False
        
        return folds

    def handle_code_lens(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri, '')
        if not text:
            return []
        
        lenses = []
        lines = text.split('\n')
        
        for i, sym in enumerate([s for s in [sym for syms in self.symbols.values() for sym in syms] if sym.uri == uri]):
            if sym.kind == 'function':
                # Show function signature as code lens
                param_hint = f"({', '.join(sym.params)})" if sym.params else "()"
                lenses.append({
                    'range': {
                        'start': {'line': sym.line, 'character': 0},
                        'end': {'line': sym.line, 'character': len(lines[sym.line]) if sym.line < len(lines) else 0}
                    },
                    'code': f"fn {sym.name}{param_hint}",
                    'command': {
                        'title': f"▶ Run function",
                        'command': "ado.runFunction",
                        'arguments': [sym.name]
                    }
                })
        
        return lenses

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

        # Add special syntax snippets
        items.append({
            'label': 'slice',
            'kind': 14,
            'detail': 'array slice syntax',
            'insertText': 'arr[${1:start}..${2:end}]',
            'insertTextFormat': 2  # Snippet
        })
        
        items.append({
            'label': 'listcomp',
            'kind': 14,
            'detail': 'list comprehension',
            'insertText': '[for ${1:i} in ${2:start}..${3:end} ${4:expr}]',
            'insertTextFormat': 2  # Snippet
        })
        
        items.append({
            'label': 'destruct',
            'kind': 14,
            'detail': 'destructuring',
            'insertText': 'let [${1:a}, ${2:b}, ...${3:rest}] = ${4:arr}',
            'insertTextFormat': 2  # Snippet
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

    def handle_document_highlight(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        line = msg['params']['position']['line']
        col = msg['params']['position']['character']

        word = self.get_symbol_at_pos(uri, line, col)
        if not word: return []

        sym = self.resolve_symbol(uri, word, line, col)
        if not sym: return []

        refs = self.find_references(word, restrict_uri=uri, restrict_sym=sym)
        highlights = []
        for ref in refs:
            highlights.append({
                'range': ref['range'],
                'kind': 1 # Text
            })
        return highlights

    def handle_inlay_hint(self, msg: dict) -> list:
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri)
        if not text: return []

        masked_text = self._mask_text(text)
        lines = masked_text.split('\n')

        start_line = msg['params']['range']['start']['line']
        end_line = msg['params']['range']['end']['line']

        hints = []
        call_pattern = re.compile(r'\b(\w+)\s*\(')

        for i in range(start_line, min(end_line + 1, len(lines))):
            line = lines[i]
            for match in call_pattern.finditer(line):
                func_name = match.group(1)
                if func_name in self.symbols:
                    sym = self.symbols[func_name][0]
                    if sym.kind == 'function' and sym.params:
                        # Simple heuristic: find commas to place parameter hints
                        args_start = match.end()
                        paren_count = 1
                        arg_idx = 0
                        current_pos = args_start

                        # Add first parameter hint right after opening parenthesis
                        if arg_idx < len(sym.params):
                            # Skip leading whitespace
                            while current_pos < len(line) and line[current_pos].isspace():
                                current_pos += 1
                            if current_pos < len(line) and line[current_pos] != ')':
                                hints.append({
                                    'position': {'line': i, 'character': current_pos},
                                    'label': f"{sym.params[arg_idx]}: ",
                                    'kind': 2, # Parameter
                                    'paddingRight': True
                                })
                                arg_idx += 1

                        while current_pos < len(line) and paren_count > 0:
                            char = line[current_pos]
                            if char == '(': paren_count += 1
                            elif char == ')': paren_count -= 1
                            elif char == ',' and paren_count == 1:
                                if arg_idx < len(sym.params):
                                    hint_pos = current_pos + 1
                                    while hint_pos < len(line) and line[hint_pos].isspace():
                                        hint_pos += 1
                                    hints.append({
                                        'position': {'line': i, 'character': hint_pos},
                                        'label': f"{sym.params[arg_idx]}: ",
                                        'kind': 2, # Parameter
                                        'paddingRight': True
                                    })
                                    arg_idx += 1
                            current_pos += 1
        return hints

    def handle_semantic_tokens_full(self, msg: dict) -> dict:
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri)
        if not text: return {'data': []}

        masked_text = self._mask_text(text)
        lines = masked_text.split('\n')

        tokens = []
        token_types = {
            'keyword': 0,
            'function': 1,
            'variable': 2,
            'parameter': 3,
            'operator': 4,
            'string': 5,
            'number': 6,
            'comment': 7
        }

        for i, (line, orig_line) in enumerate(zip(lines, text.split('\n'))):
            # Find keywords
            for kw in self.keywords:
                for match in re.finditer(r'\b' + re.escape(kw) + r'\b', line):
                    tokens.append((i, match.start(), match.end() - match.start(), token_types['keyword'], 0))

            # Find special operators: .. and ...
            for match in re.finditer(r'\.\.', line):
                tokens.append((i, match.start(), match.end() - match.start(), token_types['operator'], 0))
            for match in re.finditer(r'\.\.\.', line):
                tokens.append((i, match.start(), match.end() - match.start(), token_types['operator'], 0))

            # Find list comprehension pattern
            listcomp_match = re.search(r'\[\s*for\s+\w+\s+in', line)
            if listcomp_match:
                for match in re.finditer(r'\[', line):
                    tokens.append((i, match.start(), match.end() - match.start(), token_types['keyword'], 0))

            # Find destructuring patterns in let statements
            destruct_match = re.search(r'let\s*\[\s*', line)
            if destruct_match:
                # Highlight variable names in destructuring
                for match in re.finditer(r'\[([^\]]+)\]', line):
                    names_str = match.group(1)
                    parts = [p.strip() for p in names_str.split(',')]
                    for part in parts:
                        if '...' in part:
                            m = re.search(r'(\w+)', part)
                            if m:
                                tokens.append((i, match.start() + names_str.find(m.group(1)), 
                                    m.end() - m.start(), token_types['variable'], 0))
                        elif re.match(r'^\w+$', part):
                            tokens.append((i, match.start() + names_str.find(part), 
                                len(part), token_types['variable'], 0))

            # Find symbols
            for sym_name, sym_list in self.symbols.items():
                if sym_name in self.keywords: continue
                sym = sym_list[0]
                for match in re.finditer(r'\b' + re.escape(sym_name) + r'\b', line):
                    t_type = token_types.get(sym.kind, 2)
                    tokens.append((i, match.start(), match.end() - match.start(), t_type, 0))

        # Sort tokens by line and column
        tokens.sort(key=lambda t: (t[0], t[1]))

        # Calculate relative positions
        data = []
        prev_line = 0
        prev_start = 0

        for line, start, length, t_type, t_mod in tokens:
            delta_line = line - prev_line
            delta_start = start if delta_line > 0 else start - prev_start

            data.extend([delta_line, delta_start, length, t_type, t_mod])

            prev_line = line
            prev_start = start

        return {'data': data}

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
                },
                'semanticTokensProvider': {
                    'legend': {
                        'tokenTypes': ['keyword', 'function', 'variable', 'parameter', 'operator', 'string', 'number', 'comment'],
                        'tokenModifiers': []
                    },
                    'full': True
                },
                'inlayHintProvider': True,
                'documentHighlightProvider': True,
                'foldingRangeProvider': True,
                'callHierarchyProvider': True
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
                elif method == 'textDocument/foldingRange': result = self.handle_folding_range(msg)
                elif method == 'textDocument/semanticTokens/full': result = self.handle_semantic_tokens_full(msg)
                elif method == 'textDocument/inlayHint': result = self.handle_inlay_hint(msg)
                elif method == 'textDocument/documentHighlight': result = self.handle_document_highlight(msg)
                elif method == 'textDocument/prepareCallHierarchy': result = self.handle_prepare_call_hierarchy(msg)
                elif method == 'callHierarchy/incomingCalls': result = self.handle_call_hierarchy_incoming(msg)
                elif method == 'callHierarchy/outgoingCalls': result = self.handle_call_hierarchy_outgoing(msg)
                elif method == 'shutdown': result = None
                elif method == 'exit': break
                if 'id' in msg: self.send({'id': msg['id'], 'result': result})
            except Exception as e:
                if 'id' in msg: self.send({'id': msg['id'], 'error': {'code': -32603, 'message': str(e)}})

if __name__ == '__main__':
    AdoLSP().run()
