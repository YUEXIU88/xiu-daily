"""Patch V63: improve install guide for desktop PWA installation.

Replace installStatusHtml() and doInstallApp() with versions that
include explicit desktop steps for Chrome / Edge / Brave browsers.
Uses real UTF-8 emoji (not \\uXXXX escapes) to match file's storage style.
Safe-write: write .tmp, verify, atomic replace.
"""
import os, shutil, sys

ROOT = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences"
HTML = os.path.join(ROOT, "index.html")

# Old strings (must match exactly in file)
OLD_INSTALL_STATUS = 'function installStatusHtml(){if(isStandalone())return \'✅ 已经安装成功，你现在就是在 App 里使用！\';var ua=(navigator.userAgent||\'\').toLowerCase();if(/iphone|ipad|ipod/.test(ua))return \'iPhone / iPad：请用 <b>Safari</b> 打开本页面，点底部「分享 ⬆️」按钮 →「添加到主屏幕」，桌面即出现 App 图标。\';if(deferredInstall)return \'点下方按钮，一键安装到手机桌面 / 电脑开始菜单。\';return \'安卓手机：点浏览器右上角菜单「⋮」→「安装应用」或「添加到主屏幕」。\';}'

OLD_DO_INSTALL = 'function doInstallApp(){if(isStandalone()){showToast(\'已经安装啦，就在 App 里\');return;}if(deferredInstall){deferredInstall.prompt();deferredInstall.userChoice.then(function(){deferredInstall=null;});return;}var ua=(navigator.userAgent||\'\').toLowerCase();if(/iphone|ipad|ipod/.test(ua)){showToast(\'Safari 分享按钮 ⬆️ → 添加到主屏幕\');}else{showToast(\'浏览器菜单 ⋮ → 安装应用 / 添加到主屏幕\');}}'

# New strings (with desktop PWA instructions)
NEW_INSTALL_STATUS = (
    'function installStatusHtml(){'
    'if(isStandalone())return \'✅ 已经安装成功，你现在就是在 App 里使用！\';'
    'var ua=(navigator.userAgent||\'\').toLowerCase();'
    'if(/iphone|ipad|ipod/.test(ua))return \'iPhone / iPad：请用 <b>Safari</b> 打开本页面，点底部「分享 ⬆️」按钮 →「添加到主屏幕」，桌面即出现 App 图标。\';'
    'if(/android/.test(ua))return \'安卓手机：点浏览器右上角菜单「⋮」→「安装应用」或「添加到主屏幕」。\';'
    'if(deferredInstall)return \'点下方按钮，一键安装到桌面（电脑开始菜单 / 手机桌面）。\';'
    'return \'<b>💻 电脑端</b>（Chrome / Edge / Brave）：① 地址栏右侧会出现「📥 安装」小图标，直接点击即可安装到桌面；② 或点浏览器右上角「⋮」→「<b>安装 XIU DAILY</b>」（部分浏览器是「保存并分享 → 安装页面为应用」）。安装完后，<b>桌面 / 开始菜单</b>会出现 App 图标，双击直接打开，全屏显示、无地址栏，跟本地 App 一样用。\';}'
)

NEW_DO_INSTALL = (
    'function doInstallApp(){'
    'if(isStandalone()){showToast(\'已经安装啦，就在 App 里\');return;}'
    'if(deferredInstall){deferredInstall.prompt();deferredInstall.userChoice.then(function(){deferredInstall=null;});return;}'
    'var ua=(navigator.userAgent||\'\').toLowerCase();'
    'if(/iphone|ipad|ipod/.test(ua)){showToast(\'Safari 分享按钮 ⬆️ → 添加到主屏幕\');return;}'
    'if(/android/.test(ua)){showToast(\'浏览器右上角 ⋮ → 安装应用 / 添加到主屏幕\');return;}'
    'if(/win|mac|linux|cros/.test(ua)){showToast(\'地址栏右侧的「📥 安装」图标，或菜单 ⋮ → 安装 XIU DAILY\');return;}'
    'showToast(\'浏览器菜单 ⋮ → 安装应用 / 添加到主屏幕\');}'
)

def main():
    if not os.path.exists(HTML):
        print(f'ERROR: {HTML} not found')
        sys.exit(1)

    with open(HTML, 'r', encoding='utf-8') as f:
        data = f.read()

    orig_len = len(data)

    # Sanity check both old strings exist
    if OLD_INSTALL_STATUS not in data:
        print('ERROR: OLD_INSTALL_STATUS not found - abort (would not match)')
        sys.exit(1)
    if OLD_DO_INSTALL not in data:
        print('ERROR: OLD_DO_INSTALL not found - abort (would not match)')
        sys.exit(1)

    # Apply replacements
    new_data = data.replace(OLD_INSTALL_STATUS, NEW_INSTALL_STATUS, 1)
    new_data = new_data.replace(OLD_DO_INSTALL, NEW_DO_INSTALL, 1)

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

    # Verify size grew (we added desktop instructions, so new >= old)
    new_len = os.path.getsize(tmp)
    if new_len < orig_len:
        print(f'ERROR: new file {new_len} < orig {orig_len}')
        os.remove(tmp)
        sys.exit(1)

    shutil.move(tmp, HTML)
    print(f'OK: replaced installStatusHtml & doInstallApp')
    print(f'File size: {orig_len} -> {new_len} bytes (delta +{new_len-orig_len})')

if __name__ == '__main__':
    main()
