"""V64 step 3: Replace sp-orders code (renderOrdersTable, showOrderForm, saveOrder, etc.)
Replaces everything from '// ---------- Shopee: Orders ----------' to just before '// ---------- Shopee: Stats ----------'
with the new v64_orders.js content.
Safe write: tmp file + verify + atomic move.
"""
import os, shutil, sys

ROOT = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences"
HTML = os.path.join(ROOT, "index.html")
JS_FILE = os.path.join(ROOT, "v64_orders.js")

START_MARKER = "// ---------- Shopee: Orders ----------"
END_MARKER = "// ---------- Shopee: Stats ----------"

def main():
    if not os.path.exists(HTML):
        print(f'ERROR: {HTML} not found')
        sys.exit(1)
    if not os.path.exists(JS_FILE):
        print(f'ERROR: {JS_FILE} not found')
        sys.exit(1)

    with open(HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        new_code = f.read()

    orig_len = len(html)

    start_idx = html.find(START_MARKER)
    if start_idx < 0:
        print(f'ERROR: start marker not found')
        sys.exit(1)

    end_idx = html.find(END_MARKER, start_idx)
    if end_idx < 0:
        print(f'ERROR: end marker not found')
        sys.exit(1)

    # Check if already replaced (v64 marker)
    if '// V64' in html[start_idx:end_idx] or 'calcOrderDerived' in html:
        print('SKIP: sp-orders already replaced with V64 version')
        # Still continue if the old renderOrdersTable exists
        if 'function calcOrderDerived' in html:
            sys.exit(0)

    # Replace: new code + 2 newlines before END_MARKER
    new_html = html[:start_idx] + new_code.rstrip() + '\n\n' + html[end_idx:]

    # Safe write
    tmp = HTML + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(new_html)

    if not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
        print('ERROR: tmp file is empty/missing')
        if os.path.exists(tmp):
            os.remove(tmp)
        sys.exit(1)

    new_len = os.path.getsize(tmp)
    shutil.move(tmp, HTML)
    print(f'OK: sp-orders replaced with V64 version')
    print(f'File size: {orig_len} -> {new_len} bytes (delta {new_len-orig_len:+d})')

if __name__ == '__main__':
    main()
