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
        
        for i, line in enumerate(lines):
            match = re.search(r'fn\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                name = match.group(1)
                params_str = match.group(2)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                col = match.start(1)
                brace_count = 0
                end_line = i
                started = False
                for j in range(i, len(lines)):
                    if '{' in lines[j]: started = True
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if started and brace_count == 0:
                        end_line = j
                        break
                docstring = ""
                for k in range(i-1, -1, -1):
                    if lines[k].strip().startswith('#'):
                        docstring = lines[k].strip()[1:].strip() + " " + docstring
                    elif lines[k].strip() == "": continue
                    else: break
                symbols.append(Symbol(name=name, kind='function', uri=uri,
                    line=i, col=col, end_line=end_line, end_col=len(lines[end_line]),
                    params=params, docstring=docstring.strip()))
                for param in params:
                    param_match = re.search(r'\b' + re.escape(param) + r'\b', line)
                    if param_match:
                        symbols.append(Symbol(name=param, kind='parameter', uri=uri,
                            line=i, col=param_match.start(), end_line=i, end_col=param_match.end()))
        
        for i, line in enumerate(lines):
            match = re.search(r'let\s+(\w+)\s*=', line)
            if match:
                symbols.append(Symbol(name=match.group(1), kind='variable', uri=uri,
                    line=i, col=match.start(1), end_line=i, end_col=match.end(1)))
        
        for sym in symbols:
            if sym.name not in self.symbols: self.symbols[sym.name] = []
            self.symbols[sym.name] = [s for s in self.symbols[sym.name] if s.uri != uri]
            self.symbols[sym.name].append(sym)
    
    def get_diagnostics(self, uri: str, text: str) -> List[dict]:
        diagnostics = []
        lines = text.split('\n')
        brace_stack = []
        for i, line in enumerate(lines):
            if re.search(r'\blet\s+\w+\s*$', line):
                diagnostics.append({'range': {'start': {'line': i, 'character': 0},
                    'end': {'line': i, 'character': len(line)}}, 'severity': 1,
                    'message': 'let statement requires assignment', 'source': 'ado-lsp'})
            for j, char in enumerate(line):
                if char == '{': brace_stack.append((i, j))
                elif char == '}':
                    if brace_stack: brace_stack.pop()
                    else: diagnostics.append({'range': {'start': {'line': i, 'character': j},
                        'end': {'line': i, 'character': j+1}}, 'severity': 1,
                        'message': 'Unexpected closing brace', 'source': 'ado-lsp'})
            for match in re.finditer(r'(\w+)\s*\(', line):
                func = match.group(1)
                if func not in self.keywords and func not in self.builtins:
                    if func not in self.symbols or not any(s.kind == 'function' for s in self.symbols[func]):
                        diagnostics.append({'range': {'start': {'line': i, 'character': match.start(1)},
                            'end': {'line': i, 'character': match.end(1)}}, 'severity': 2,
                            'message': f"Undefined function '{func}'", 'source': 'ado-lsp'})
        if brace_stack:
            diagnostics.append({'range': {'start': {'line': brace_stack[-1][0], 'character': brace_stack[-1][1]},
                'end': {'line': brace_stack[-1][0], 'character': brace_stack[-1][1]+1}}, 'severity': 1,
                'message': 'Unclosed brace', 'source': 'ado-lsp'})
        return diagnostics
    
    def find_word_at(self, uri: str, line: int, col: int) -> Tuple[str, int, int]:
        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if line >= len(lines): return "", col, col
        line_text = lines[line]
        start = col
        while start > 0 and (line_text[start-1].isalnum() or line_text[start-1] == '_'): start -= 1
        end = col
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == '_'): end += 1
        return line_text[start:end], start, end
    
    def find_references(self, uri: str, line: int, col: int) -> List[Reference]:
        word, _, _ = self.find_word_at(uri, line, col)
        if not word: return []
        refs = []
        for doc_uri, doc_text in self.docs.items():
            for i, doc_line in enumerate(doc_text.split('\n')):
                for match in re.finditer(r'\b' + re.escape(word) + r'\b', doc_line):
                    refs.append(Reference(uri=doc_uri, line=i, col=match.start(), end_col=match.end()))
        return refs
    
    def find_definition(self, uri: str, line: int, col: int) -> Optional[Symbol]:
        word, _, _ = self.find_word_at(uri, line, col)
        if not word: return None
        if word in self.symbols:
            for sym in self.symbols[word]:
                if sym.kind in ['function', 'variable', 'parameter']: return sym
        return None
    
    def format_document(self, text: str) -> str:
        lines = text.split('\n')
        formatted = []
        indent = 0
        for line in lines:
            stripped = line.strip()
            if not stripped: formatted.append(''); continue
            if stripped.startswith('}'): indent = max(0, indent - 1)
            formatted.append('  ' * indent + stripped)
            indent += stripped.count('{') - stripped.count('}')
        return '\n'.join(formatted)
    
    def send(self, msg):
        content = json.dumps(msg)
        sys.stdout.buffer.write(f"Content-Length: {len(content)}\r\n\r\n{content}".encode())
        sys.stdout.buffer.flush()
    
    def recv(self):
        headers = {}
        while True:
            line = sys.stdin.buffer.readline().decode().strip()
            if not line: break
            if ': ' in line: headers[line.split(': ', 1)[0]] = line.split(': ', 1)[1]
        if 'Content-Length' not in headers: return None
        return json.loads(sys.stdin.buffer.read(int(headers['Content-Length'])).decode())
    
    def handle_initialize(self, msg):
        return {'capabilities': {
            'textDocumentSync': 1,
            'completionProvider': {'triggerCharacters': ['.'], 'completionItem': {'snippetSupport': True}},
            'definitionProvider': True, 'typeDefinitionProvider': True, 'referencesProvider': True,
            'hoverProvider': True, 'documentFormattingProvider': True, 'documentRangeFormattingProvider': True,
            'renameProvider': {'prepareProvider': True}, 'documentSymbolProvider': True, 'workspaceSymbolProvider': True,
            'codeActionProvider': {'codeActionKinds': ['quickfix', 'refactor', 'source.fixAll']},
            'codeLensProvider': {'resolveProvider': False},
            'signatureHelpProvider': {'triggerCharacters': ['(', ',']},
            'diagnosticProvider': {'interFileDependencies': True, 'workspaceDiagnostics': False}
        }, 'serverInfo': {'name': 'ado-lsp', 'version': '1.0.0'}}
    
    def handle_completion(self, msg):
        items = []
        for kw in self.keywords: items.append({'label': kw, 'kind': 14, 'detail': 'keyword'})
        items.append({'label': 'print', 'kind': 3, 'detail': 'fn print(...values)', 'insertText': 'print($1)', 'insertTextFormat': 2})
        for name, syms in self.symbols.items():
            for sym in syms:
                if sym.kind == 'function':
                    params = sym.params or []
                    items.append({'label': name, 'kind': 3,
                        'detail': f"fn {name}({', '.join(params)})",
                        'documentation': sym.docstring or f"Function at line {sym.line + 1}",
                        'insertText': f"{name}({', '.join(f'${{{i+1}:{p}}}' for i,p in enumerate(params))})" if params else f"{name}($1)",
                        'insertTextFormat': 2})
                    break
                elif sym.kind == 'variable':
                    items.append({'label': name, 'kind': 6, 'detail': 'variable'})
                    break
        return {'items': items, 'isIncomplete': False}
    
    def handle_definition(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        sym = self.find_definition(uri, pos['line'], pos['character'])
        if sym: return {'uri': sym.uri, 'range': {'start': {'line': sym.line, 'character': sym.col},
            'end': {'line': sym.line, 'character': sym.end_col}}}
        return None
    
    def handle_references(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        refs = self.find_references(uri, pos['line'], pos['character'])
        return [{'uri': r.uri, 'range': {'start': {'line': r.line, 'character': r.col},
            'end': {'line': r.line, 'character': r.end_col}}} for r in refs]
    
    def handle_hover(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        sym = self.find_definition(uri, pos['line'], pos['character'])
        if sym:
            kind_label = {'function': 'fn', 'variable': 'let', 'parameter': 'param'}.get(sym.kind, '')
            if sym.kind == 'function':
                params = ', '.join(sym.params) if sym.params else ''
                doc = f"```ado\nfn {sym.name}({params})\n```\n\n{sym.docstring or ''}"
            else:
                doc = f"```ado\n{kind_label} {sym.name}\n```\n\nDefined at line {sym.line + 1}"
            return {'contents': {'kind': 'markdown', 'value': doc}}
        return None
    
    def handle_signature_help(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        text = self.docs.get(uri, '')
        lines = text.split('\n')
        if pos['line'] >= len(lines): return None
        match = re.search(r'(\w+)\s*\(([^)]*)$', lines[pos['line']][:pos['character']])
        if not match: return None
        func = match.group(1)
        arg_num = match.group(2).count(',')
        if func in self.symbols:
            for sym in self.symbols[func]:
                if sym.kind == 'function':
                    return {'signatures': [{'label': f"{func}({', '.join(sym.params)})",
                        'parameters': [{'label': p} for p in sym.params] if sym.params else [],
                        'activeParameter': min(arg_num, len(sym.params) - 1) if sym.params else 0}],
                        'activeSignature': 0, 'activeParameter': 0}
        return None
    
    def handle_formatting(self, msg):
        uri = msg['params']['textDocument']['uri']
        text = self.docs.get(uri, '')
        formatted = self.format_document(text)
        lines = text.split('\n')
        return [{'range': {'start': {'line': 0, 'character': 0}, 'end': {'line': len(lines), 'character': 0}},
            'newText': formatted}]
    
    def handle_rename(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        new_name = msg['params']['newName']
        refs = self.find_references(uri, pos['line'], pos['character'])
        changes = {}
        for r in refs:
            if r.uri not in changes: changes[r.uri] = []
            changes[r.uri].append({'range': {'start': {'line': r.line, 'character': r.col},
                'end': {'line': r.line, 'character': r.end_col}}, 'newText': new_name})
        return {'changes': changes}
    
    def handle_prepare_rename(self, msg):
        uri = msg['params']['textDocument']['uri']
        pos = msg['params']['position']
        word, start, end = self.find_word_at(uri, pos['line'], pos['character'])
        if not word: return None
        return {'range': {'start': {'line': pos['line'], 'character': start},
            'end': {'line': pos['line'], 'character': end}}, 'placeholder': word}
    
    def handle_document_symbols(self, msg):
        uri = msg['params']['textDocument']['uri']
        symbols = []
        kind_map = {'function': 12, 'variable': 13, 'parameter': 6}
        for name, syms in self.symbols.items():
            for sym in syms:
                if sym.uri == uri:
                    symbols.append({'name': sym.name, 'kind': kind_map.get(sym.kind, 13),
                        'range': {'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.end_line, 'character': sym.end_col}},
                        'selectionRange': {'start': {'line': sym.line, 'character': sym.col},
                            'end': {'line': sym.line, 'character': sym.col + len(sym.name)}}})
        return sorted(symbols, key=lambda s: s['range']['start']['line'])
    
    def handle_workspace_symbols(self, msg):
        query = msg['params'].get('query', '').lower()
        symbols = []
        kind_map = {'function': 12, 'variable': 13}
        for name, syms in self.symbols.items():
            if query and query not in name.lower(): continue
            for sym in syms:
                symbols.append({'name': sym.name, 'kind': kind_map.get(sym.kind, 13),
                    'location': {'uri': sym.uri, 'range': {'start': {'line': sym.line, 'character': sym.col},
                        'end': {'line': sym.line, 'character': sym.col + len(sym.name)}}}})
        return symbols[:100]
    
    def handle_code_action(self, msg):
        uri = msg['params']['textDocument']['uri']
        context = msg['params']['context']
        actions = []
        for diag in context.get('diagnostics', []):
            if 'Undefined function' in diag.get('message', ''):
                match = re.search(r"'(\w+)'", diag['message'])
                if match:
                    func = match.group(1)
                    actions.append({'title': f"Create function '{func}'",
                        'kind': 'quickfix', 'diagnostics': [diag],
                        'edit': {'changes': {uri: [{'range': {'start': {'line': 999999, 'character': 0},
                            'end': {'line': 999999, 'character': 0}}, 'newText': f"\nfn {func}() {{\n  \n}}\n"}]}}})
        return actions
    
    def handle_code_lens(self, msg):
        uri = msg['params']['textDocument']['uri']
        lenses = []
        text = self.docs.get(uri, '')
        for name, syms in self.symbols.items():
            for sym in syms:
                if sym.uri == uri and sym.kind == 'function':
                    refs = len(self.find_references(uri, sym.line, sym.col))
                    lenses.append({'range': {'start': {'line': sym.line, 'character': sym.col},
                        'end': {'line': sym.line, 'character': sym.col + len(sym.name)}},
                        'command': {'title': f'{refs} references', 'command': 'ado.showReferences',
                            'arguments': [uri, sym.line, sym.col]}})
        return lenses
    
    def publish_diagnostics(self, uri: str):
        text = self.docs.get(uri, '')
        diagnostics = self.get_diagnostics(uri, text)
        self.send({'method': 'textDocument/publishDiagnostics', 'params': {'uri': uri, 'diagnostics': diagnostics}})
    
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
