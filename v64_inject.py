"""V64 step 2: Inject 3 new modules (Purchase / Stock / Ads) before MODULES['sp-stats'].
Reads v64_new_modules.js and inserts its content before the sp-stats module definition.
Safe write: tmp file + verify + atomic move.
"""
import os, shutil, sys

ROOT = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences"
HTML = os.path.join(ROOT, "index.html")
JS_FILE = os.path.join(ROOT, "v64_new_modules.js")

INJECT_MARKER = "MODULES['sp-stats']"

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
        js_code = f.read()

    orig_len = len(html)

    # Find injection point
    idx = html.find(INJECT_MARKER)
    if idx < 0:
        print(f'ERROR: injection marker "{INJECT_MARKER}" not found')
        sys.exit(1)

    # Check if already injected
    if 'MODULES[\'sp-purchase\']' in html:
        print('SKIP: v64_new_modules.js already injected (sp-purchase found)')
        sys.exit(0)

    # Inject: insert JS code + 2 newlines before MODULES['sp-stats']
    new_html = html[:idx] + js_code.rstrip() + '\n\n' + html[idx:]

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
    print(f'OK: 3 new modules injected (purchase/stock/ads)')
    print(f'File size: {orig_len} -> {new_len} bytes (delta +{new_len-orig_len})')

if __name__ == '__main__':
    main()
