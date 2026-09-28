import re

def check_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    print(f"Total lines: {len(lines)}, Total chars: {len(content)}")

    # Check bracket balance
    open_braces = 0
    in_comment = False
    brace_stack = []

    for i, line in enumerate(lines, 1):
        j = 0
        while j < len(line):
            if not in_comment and line[j:j+2] == '/*':
                in_comment = True
                j += 2
                continue
            elif in_comment and line[j:j+2] == '*/':
                in_comment = False
                j += 2
                continue
            elif in_comment:
                j += 1
                continue

            char = line[j]
            if char == '{':
                open_braces += 1
                brace_stack.append((i, j))
            elif char == '}':
                open_braces -= 1
                if open_braces < 0:
                    print(f"ERROR: Unmatched closing brace at line {i}, col {j}")
                else:
                    brace_stack.pop()
            j += 1

    if open_braces != 0:
        print(f"ERROR: Mismatched braces! Open braces count = {open_braces}")
        for line_no, col in brace_stack:
            print(f"  Unclosed brace opened at line {line_no}:{col}")
    else:
        print("PASS: Braces are perfectly balanced!")

if __name__ == '__main__':
    check_css(r'frontend/css/main.css')
