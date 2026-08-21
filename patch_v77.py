"""
V77: 整个 SKU 行强制单行（sku-name + 成本 + 所有站点 横向排列不换行）
"""
SRC='C:/Users/92809/WorkBuddy/2026-08-19-23-27-21/english-sentences/index.html'

with open(SRC,'r',encoding='utf-8') as f:
    src=f.read()

# 1) CSS: .sp-pp-sku-line 强制 nowrap + overflow-x:auto (过宽时横向滚动)
old='.sp-pp-sku-line{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:10.5px;line-height:1.6;width:100%}'
new='.sp-pp-sku-line{display:flex;align-items:center;gap:5px;flex-wrap:nowrap;font-size:10.5px;line-height:1.6;width:100%;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;padding:1px 0}'
assert src.count(old)==1,'sp-pp-sku-line CSS 未匹配'
src=src.replace(old,new)

# 2) CSS: 隐藏 sp-pp-sku-line 的滚动条但保留滚动能力
src=src.replace(
    '.sp-pp-date-line{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:10px;color:var(--text-3);margin-top:2px;padding-top:2px;border-top:1px dashed var(--border-l)}',
    '.sp-pp-sku-line::-webkit-scrollbar{height:0;display:none}.sp-pp-sku-line{scrollbar-width:thin;scrollbar-color:transparent transparent}.sp-pp-date-line{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:10px;color:var(--text-3);margin-top:2px;padding-top:2px;border-top:1px dashed var(--border-l)}'
)

# 3) CSS: .sp-pp-sku-name 缩短 (135px → 110px)，让站间有更多空间
old3='.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:6px;white-space:nowrap;flex-shrink:0;min-width:135px}'
new3='.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:4px;white-space:nowrap;flex-shrink:0;min-width:100px;max-width:130px}'
assert src.count(old3)==1,'sp-pp-sku-name 未匹配'
src=src.replace(old3,new3)

# 4) CSS: .sp-pp-site-block 进一步压紧
old4='.sp-pp-site-block{display:inline-flex;align-items:center;gap:5px;flex-shrink:0;background:var(--bg);border:1px solid var(--border-l);border-radius:8px;padding:2px 5px;white-space:nowrap;flex-wrap:nowrap}'
new4='.sp-pp-site-block{display:inline-flex;align-items:center;gap:4px;flex:0 0 auto;flex-shrink:0;background:var(--bg);border:1px solid var(--border-l);border-radius:7px;padding:2px 5px;white-space:nowrap;flex-wrap:nowrap;font-size:10.5px}'
assert src.count(old4)==1,'sp-pp-site-block 未匹配'
src=src.replace(old4,new4)

# 5) CSS: .col-img 去掉 max-width 限制，让宽内容撑开（避免 title 列挤压）
old5='.sp-prod-tbl .col-img{vertical-align:top;min-width:280px;max-width:480px;padding-top:6px;padding-left:10px;padding-right:6px}'
new5='.sp-prod-tbl .col-img{vertical-align:top;min-width:300px;max-width:560px;padding-top:6px;padding-left:10px;padding-right:6px}'
assert src.count(old5)==1,'col-img 未匹配'
src=src.replace(old5,new5)

# 6) APP_VERSION 升 77
src=src.replace('var APP_VERSION=76;','var APP_VERSION=77;')

with open(SRC,'w',encoding='utf-8') as f:
    f.write(src)

print('V77 补丁完成')
print('  sp-pp-sku-line: flex-wrap:nowrap + overflow-x:auto')
print('  sp-pp-sku-name: 135px→100-130px')
print('  sp-pp-site-block: 紧凑化 + flex:0 0 auto')
print('  col-img: max-width 480→560')
