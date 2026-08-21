"""V75: 将价格信息从标题列移到图片列下方"""
import re

path=r'C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences\index.html'
with open(path,'r',encoding='utf-8') as f:
    src=f.read()

# 1. 改 HTML 结构：prodDiscInputs + renderProductPricePreview 从 col-title 移到 col-img
#    原始：<td class="col-img">'+img+'</td><td class="col-title">'+titleWrap+(p.title&&p.title!==p.name?'<div class="sp-tb-sub">'+escapeHtml(p.name)+'</div>':'')+prodDiscInputs(p)+renderProductPricePreview(p)+'</td>
#    改为：<td class="col-img">'+img+prodDiscInputs(p)+renderProductPricePreview(p)+'</td><td class="col-title">'+titleWrap+(p.title&&p.title!==p.name?'<div class="sp-tb-sub">'+escapeHtml(p.name)+'</div>':'')+'</td>

# 用 re 定位关键模式：col-img 后跟 col-title，把中间的 price 部分移走
pattern = re.compile(
    r"(<td class=\"col-img\">'\+img\+)'</td><td class=\"col-title\">'\+titleWrap\+\(p\.title&&p\.title!==p\.name\?'<div class=\"sp-tb-sub\">'\+escapeHtml\(p\.name\)\+'</div>':''\)\+prodDiscInputs\(p\)\+renderProductPricePreview\(p\)\+'</td>",
    re.DOTALL
)
m = pattern.search(src)
assert m, 'col-img/title HTML 模式未找到'
replacement = (
    r"\1prodDiscInputs(p)+renderProductPricePreview(p)+'</td><td class=\"col-title\">'+titleWrap+(p.title&&p.title!==p.name?'<div class=\"sp-tb-sub\">'+escapeHtml(p.name)+'</div>':'')+'</td>"
)
src2 = pattern.sub(replacement, src, count=1)
assert src2 != src, '替换未生效'
src = src2

# 2. 改 col-img 宽度 90px → 440px
old2 = '.sp-prod-tbl .col-img{vertical-align:top;width:90px;padding-top:6px;padding-left:10px;padding-right:6px}'
new2 = '.sp-prod-tbl .col-img{vertical-align:top;width:440px;padding-top:6px;padding-left:10px;padding-right:6px}'
assert src.count(old2) == 1, 'col-img CSS 匹配数=%d' % src.count(old2)
src = src.replace(old2, new2)

# 3. sp-pp-bar 左边距对齐
old3 = '.sp-pp-bar{margin-top:5px;display:flex;flex-direction:column;gap:3px}'
new3 = '.sp-pp-bar{margin-top:8px;display:flex;flex-direction:column;gap:4px;align-items:flex-start}'
assert src.count(old3) == 1, 'sp-pp-bar CSS 匹配数=%d' % src.count(old3)
src = src.replace(old3, new3)

# 4. sp-pp-sku-line 全宽
old4 = '.sp-pp-sku-line{display:flex;align-items:center;gap:4px;flex-wrap:wrap;font-size:10.5px;line-height:1.5}'
new4 = '.sp-pp-sku-line{display:flex;align-items:center;gap:4px;flex-wrap:wrap;font-size:10.5px;line-height:1.6;width:100%}'
assert src.count(old4) == 1, 'sp-pp-sku-line CSS 匹配数=%d' % src.count(old4)
src = src.replace(old4, new4)

# 5. SKU 名最小宽度（实际 CSS 较长，匹配）
old5 = '.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:4px;white-space:nowrap}'
new5 = '.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:6px;white-space:nowrap;flex-shrink:0;min-width:135px}'
assert src.count(old5) == 1, 'sp-pp-sku-name CSS 匹配数=%d' % src.count(old5)
src = src.replace(old5, new5)

# 6. sp-prod-disc 也加点 margin
old6 = '.sp-prod-disc{display:flex;align-items:center;gap:6px;margin-top:6px}'
n6 = src.count(old6)
if n6 == 1:
    new6 = '.sp-prod-disc{display:flex;align-items:center;gap:6px;margin-top:8px;flex-wrap:wrap}'
    src = src.replace(old6, new6)

# 7. 同步版本号
src = src.replace('var APP_VERSION=74;', 'var APP_VERSION=75;')
src = src.replace("var CACHE='xiu-daily-v74';", "var CACHE='xiu-daily-v75';", 1)
src = src.replace('var SW_VERSION=74;', 'var SW_VERSION=75;')

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK V75 patch done')
