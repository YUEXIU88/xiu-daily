"""V64 step 1: Update NAV_TREE shopee group.
Remove sp-pricing (售价利润), add sp-purchase (采购表), sp-stock (库存表), sp-ads (广告支出).
File uses \\uXXXX literal escape sequences for Chinese - use raw strings to match exactly.
Safe write: tmp file + verify + atomic move.
"""
import os, shutil, sys

ROOT = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences"
HTML = os.path.join(ROOT, "index.html")

# Old NAV shopee group (raw strings for \uXXXX literals, normal "\n" for real newlines)
OLD_NAV = (
    r"id:'shopee',name:'Shopee\u7ba1\u7406',icon:'\ud83d\udecd\ufe0f',children:[" +
    "\n    " + r"{id:'sp-products',name:'\u4ea7\u54c1\u7ba1\u7406',icon:'\ud83d\udce6'}," +
    "\n    " + r"{id:'sp-pricing',name:'\u552e\u4ef7\u5229\u6da6',icon:'\ud83d\udc8e'}," +
    "\n    " + r"{id:'sp-orders',name:'\u8ba2\u5355\u7ba1\u7406',icon:'\ud83e\udd17'}," +
    "\n    " + r"{id:'sp-stats',name:'\u6570\u636e\u7edf\u8ba1',icon:'\ud83d\udcca'}" +
    "\n  ]},"
)

# New NAV shopee group (6 modules: products / orders / purchase / stock / ads / stats)
NEW_NAV = (
    r"id:'shopee',name:'Shopee\u7ba1\u7406',icon:'\ud83d\udecd\ufe0f',children:[" +
    "\n    " + r"{id:'sp-products',name:'\u4ea7\u54c1\u7ba1\u7406',icon:'\ud83d\udce6'}," +
    "\n    " + r"{id:'sp-orders',name:'\u8ba2\u5355\u7ba1\u7406',icon:'\ud83e\udd17'}," +
    "\n    " + r"{id:'sp-purchase',name:'\u91c7\u8d2d\u8868',icon:'\ud83d\uded2'}," +
    "\n    " + r"{id:'sp-stock',name:'\u5e93\u5b58\u8868',icon:'\ud83d\udce6'}," +
    "\n    " + r"{id:'sp-ads',name:'\u5e7f\u544a\u652f\u51fa',icon:'\ud83d\udce3'}," +
    "\n    " + r"{id:'sp-stats',name:'\u6570\u636e\u7edf\u8ba1',icon:'\ud83d\udcca'}" +
    "\n  ]},"
)

def main():
    if not os.path.exists(HTML):
        print(f'ERROR: {HTML} not found')
        sys.exit(1)

    with open(HTML, 'r', encoding='utf-8') as f:
        data = f.read()

    orig_len = len(data)

    if OLD_NAV not in data:
        # Try a more permissive search - maybe whitespace differs
        # Show the actual chars around 'shopee' for debugging
        idx = data.find("id:'shopee'")
        if idx >= 0:
            print('Found shopee at offset', idx, 'but exact OLD_NAV not matched.')
            print('Actual context (200 chars):')
            print(repr(data[idx:idx+400]))
        else:
            print("id:'shopee' not found at all!")
        sys.exit(1)

    new_data = data.replace(OLD_NAV, NEW_NAV, 1)

    if new_data == data:
        print('ERROR: no changes applied')
        sys.exit(1)

    # Safe write
    tmp = HTML + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(new_data)

    if not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
        print('ERROR: tmp file is empty/missing')
        if os.path.exists(tmp):
            os.remove(tmp)
        sys.exit(1)

    new_len = os.path.getsize(tmp)
    shutil.move(tmp, HTML)
    print(f'OK: NAV_TREE shopee group updated')
    print(f'File size: {orig_len} -> {new_len} bytes (delta {new_len-orig_len:+d})')

if __name__ == '__main__':
    main()
