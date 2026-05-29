with open("lsp/do_lsp.py") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "def run(" in line:
            print("".join(lines[i:i+40]))
            break
