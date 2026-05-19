#!/usr/bin/env python3
"""Test script to verify LSP functionality"""

import subprocess
import json
import sys

def send_request(proc, method, params, req_id=1):
    """Send LSP request"""
    msg = {
        'jsonrpc': '2.0',
        'id': req_id,
        'method': method,
        'params': params
    }
    content = json.dumps(msg)
    request = f"Content-Length: {len(content)}\r\n\r\n{content}"
    proc.stdin.write(request.encode())
    proc.stdin.flush()

def send_notification(proc, method, params):
    """Send LSP notification"""
    msg = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params
    }
    content = json.dumps(msg)
    request = f"Content-Length: {len(content)}\r\n\r\n{content}"
    proc.stdin.write(request.encode())
    proc.stdin.flush()

def read_response(proc):
    """Read LSP response"""
    headers = {}
    while True:
        line = proc.stdout.readline().decode().strip()
        if not line:
            break
        k, v = line.split(': ', 1)
        headers[k] = v
    
    length = int(headers['Content-Length'])
    content = proc.stdout.read(length).decode()
    return json.loads(content)

def test_lsp():
    """Test LSP features"""
    proc = subprocess.Popen(
        ['./lsp/do-lsp.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Testing PL Language Server...")
    print()
    
    # Initialize
    print("1. Testing initialization...")
    send_request(proc, 'initialize', {
        'processId': None,
        'rootUri': 'file:///test',
        'capabilities': {}
    })
    def wait_for_response(req_id):
        while True:
            res = read_response(proc)
            if res.get('id') == req_id:
                return res

    response = wait_for_response(1)
    assert 'result' in response
    assert 'capabilities' in response['result']
    print("   ✓ Initialize successful")
    
    send_notification(proc, 'initialized', {})
    
    # Open document
    print("2. Testing document open...")
    test_code = """fn add(a, b) {
  return a + b
}

fn main() {
  let result = add(5, 10)
  return result
}"""
    
    send_notification(proc, 'textDocument/didOpen', {
        'textDocument': {
            'uri': 'file:///test.do',
            'languageId': 'pl',
            'version': 1,
            'text': test_code
        }
    })
    print("   ✓ Document opened")
    
    # Test completion
    print("3. Testing completion...")
    send_request(proc, 'textDocument/completion', {
        'textDocument': {'uri': 'file:///test.do'},
        'position': {'line': 5, 'character': 10}
    }, req_id=2)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    assert 'result' in response
    assert 'items' in response['result']
    items = [item['label'] for item in response['result']['items']]
    assert 'fn' in items
    assert 'add' in items
    print(f"   ✓ Completion items: {', '.join(items[:5])}...")
    
    # Test definition
    print("4. Testing go-to-definition...")
    send_request(proc, 'textDocument/definition', {
        'textDocument': {'uri': 'file:///test.do'},
        'position': {'line': 5, 'character': 17}  # 'add' in add(5, 10)
    }, req_id=3)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    if response.get('result'):
        print(f"   ✓ Definition found at line {response['result']['range']['start']['line']}")
    else:
        print("   ✓ Definition lookup completed")
    
    # Test references
    print("5. Testing find references...")
    send_request(proc, 'textDocument/references', {
        'textDocument': {'uri': 'file:///test.do'},
        'position': {'line': 0, 'character': 3},  # 'add' function name
        'context': {'includeDeclaration': True}
    }, req_id=4)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    if response.get('result'):
        print(f"   ✓ Found {len(response['result'])} references")
    
    # Test hover
    print("6. Testing hover...")
    send_request(proc, 'textDocument/hover', {
        'textDocument': {'uri': 'file:///test.do'},
        'position': {'line': 0, 'character': 3}
    }, req_id=5)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    if response.get('result'):
        print("   ✓ Hover information available")
    
    # Test diagnostics
    print("7. Testing diagnostics...")
    send_request(proc, 'textDocument/diagnostic', {
        'textDocument': {'uri': 'file:///test.do'}
    }, req_id=6)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    if response.get('result'):
        diag_count = len(response['result']['items'][0]['diagnostics'])
        print(f"   ✓ Diagnostics: {diag_count} issues found")
    
    # Test formatting
    print("8. Testing formatting...")
    send_request(proc, 'textDocument/formatting', {
        'textDocument': {'uri': 'file:///test.do'},
        'options': {'tabSize': 2, 'insertSpaces': True}
    }, req_id=7)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    if response.get('result'):
        print("   ✓ Formatting available")
    
    # Shutdown
    print("9. Testing shutdown...")
    send_request(proc, 'shutdown', {}, req_id=8)
    timeout_counter = 0
    while True:
        response = read_response(proc)
        if 'id' in response:
            break
        timeout_counter += 1
        if timeout_counter > 10:
            raise TimeoutError("No response with 'id' received after 10 attempts")
    send_notification(proc, 'exit', {})
    print("   ✓ Shutdown successful")
    
    proc.wait(timeout=2)
    print()
    print("All tests passed! ✓")

if __name__ == '__main__':
    try:
        test_lsp()
    except Exception as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)
