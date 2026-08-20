import re

path = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences\index.html"
src = open(path, "r", encoding="utf-8").read()

# === 1) CSS: 图片放大 + 序号样式 + 标题不截断 + 列对齐 ===
old_css = """.sp-tb-img{width:44px;height:44px;object-fit:cover;border-radius:8px;display:block}
.sp-tb-img.ph{background:var(--bg);display:flex;align-items:center;justify-content:center;font-size:18px;color:var(--text-3)}
.sp-tb-title-wrap{display:flex;align-items:center;gap:4px;max-width:260px}
.sp-tb-title{font-weight:600;font-size:13px;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
.sp-tb-sub{font-size:11px;color:var(--text-3)}"""

new_css = """.sp-tb-img{width:72px;height:72px;object-fit:cover;border-radius:10px;display:block;border:1px solid var(--border-l);background:var(--bg)}
.sp-tb-img.ph{background:var(--bg);display:flex;align-items:center;justify-content:center;font-size:30px;color:var(--text-3)}
.sp-tb-img-wrap{padding:4px;background:var(--card);border-radius:12px;border:1px solid var(--border-l);display:inline-block}
.sp-tb-idx{font-size:11px;color:var(--text-2);font-weight:700;text-align:center;margin-bottom:4px;background:var(--primary-l);color:var(--primary);border-radius:10px;padding:1px 0;letter-spacing:.5px}
.sp-tb-title-wrap{display:flex;align-items:center;gap:6px;width:100%}
.sp-tb-title{font-weight:700;font-size:13.5px;line-height:1.4;white-space:nowrap;overflow:visible;color:var(--text);flex:1;min-width:0}
.sp-tb-title-copy{flex:0 0 auto;background:var(--primary-l);border:1px solid var(--primary);color:var(--primary);border-radius:7px;padding:3px 8px;font-size:12px;cursor:pointer;font-weight:600;transition:all .15s ease}
.sp-tb-title-copy:hover{background:var(--primary);color:#fff}
.sp-tb-sub{font-size:11px;color:var(--text-3);margin-top:1px}"""

assert old_css in src, "CSS block not found"
src = src.replace(old_css, new_css)

# === 2) CSS: col-img 列宽 + 调整列对齐 + SKU 列表左对齐图片 ===
old_col = """.sp-prod-tbl .col-sku{min-width:96px}"""
new_col = """.sp-prod-tbl .col-img{vertical-align:top;width:90px;padding-top:6px;padding-left:10px;padding-right:6px}
.sp-prod-tbl .col-title{vertical-align:top;padding-top:4px;padding-left:4px}
.sp-prod-tbl .col-sku{min-width:64px}
.sp-pp-bar{margin-top:6px;margin-left:0;padding-left:0;display:flex;flex-direction:column;gap:4px}"""
assert old_col in src
src = src.replace(old_col, new_col)

# === 3) .sp-pp-sku-name 去掉 max-width 让 SKU 号完整展示 ===
old_sku_name = """.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:280px;overflow-wrap:anywhere;padding-right:6px;border-right:1px dashed var(--border-l);margin-right:2px}"""
new_sku_name = """.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:4px;white-space:nowrap}"""
assert old_sku_name in src
src = src.replace(old_sku_name, new_sku_name)

# === 4) 删除 col-idx 在小屏隐藏规则中的引用（避免报错） — 查找 col-idx 相关 CSS ===
# 保留兼容：在折叠后 colspan 仍用 6

# === 5) renderProductGrid: 1) 去掉 col-idx 表头；2) 把序号移到 col-img 内；3) titleWrap 只剩复制按钮 ===
old_head = """var head='<thead><tr><th class="col-idx">#</th><th class="col-img">图片</th><th class="col-title">上架标题 / 产品名</th><th class="col-cat">类目</th><th class="col-sku">SKU</th><th class="col-status">状态</th><th class="col-act">操作</th></tr></thead>';"""

new_head = """var head='<thead><tr><th class="col-img" style="width:90px">图片</th><th class="col-title">上架标题 / 产品名</th><th class="col-cat">类目</th><th class="col-sku">SKU</th><th class="col-status">状态</th><th class="col-act">操作</th></tr></thead>';"""
assert old_head in src, "head not found"
src = src.replace(old_head, new_head)

# === 6) img 标签包到 .sp-tb-img-wrap 内 + 上方加序号 ===
old_img = """var img=p.img?'<img class="sp-tb-img" src="'+escapeAttr(p.img)+'" onerror="this.style.display=\\'none\\'">':'<div class="sp-tb-img ph">📦</div>';"""
new_img = """var imgCore=p.img?'<img class="sp-tb-img" src="'+escapeAttr(p.img)+'" onerror="this.style.display=\\'none\\'">':'<div class="sp-tb-img ph">📦</div>';
    var img='<div class="sp-tb-idx">#'+(idx+1)+'</div><div class="sp-tb-img-wrap">'+imgCore+'</div>';"""
assert old_img in src
src = src.replace(old_img, new_img)

# === 7) titleWrap：去掉 expandTitle，只剩一个明显的复制按钮 ===
old_titlewrap = """var fullT=escapeHtml(p.title||p.name);
    var titleWrap='<div class="sp-tb-title-wrap"><div class="sp-tb-title" title="'+escapeAttr(p.title||p.name)+'">'+fullT+'</div><button class="act-btn" data-act="expandTitle" title="展开完整标题">📄</button><button class="act-btn" data-act="copyTitle" title="复制标题">📋</button></div>';"""
new_titlewrap = """var fullT=escapeHtml(p.title||p.name);
    var titleWrap='<div class="sp-tb-title-wrap"><div class="sp-tb-title" title="'+escapeAttr(p.title||p.name)+'">'+fullT+'</div><button class="sp-tb-title-copy" data-act="copyTitle" title="复制标题到剪贴板">📋 复制</button></div>';"""
assert old_titlewrap in src
src = src.replace(old_titlewrap, new_titlewrap)

# === 8) 整行 tr: 删除 <td class="num col-idx">'+(idx+1)+'</td> ===
old_row = """return '<tr data-pid="'+p.id+'" class="sp-main-row'+(exp?' exp':'')+'"><td class="num col-idx">'+(idx+1)+'</td><td class="col-img">'+img+'</td><td class="col-title">'+titleWrap+(p.title&&p.title!==p.name?'<div class="sp-tb-sub">'+escapeHtml(p.name)+'</div>':'')+prodDiscInputs(p)+renderProductPricePreview(p)+'</td><td class="col-cat">'+(p.category?escapeHtml(p.category):'<span style="color:var(--text-3)">—</span>')+'</td><td class="col-sku"><div class="sp-tb-skunum">'+skuN+'</div></td><td class="col-status">'+prodStatusBadge(p.status)+'</td><td class="col-act">'+actions+'</td></tr>'+
      '<tr class="sp-detail-row'+(exp?' open':'')+'" data-pid="'+p.id+'"><td colspan="7"><div class="sp-detail-wrap">'+
        '<div class="sp-detail-title">💸 成本 / 重量</div>'+prodCostWeightHtml(p)+
        '<div class="sp-detail-title" style="margin-top:10px">🔢 SKU 明细（'+skuN+'）</div>'+
        renderSkuDetailTable(p)+
      '</div></td></tr>';"""
new_row = """return '<tr data-pid="'+p.id+'" class="sp-main-row'+(exp?' exp':'')+'"><td class="col-img">'+img+'</td><td class="col-title">'+titleWrap+(p.title&&p.title!==p.name?'<div class="sp-tb-sub">'+escapeHtml(p.name)+'</div>':'')+prodDiscInputs(p)+renderProductPricePreview(p)+'</td><td class="col-cat">'+(p.category?escapeHtml(p.category):'<span style="color:var(--text-3)">—</span>')+'</td><td class="col-sku"><div class="sp-tb-skunum">'+skuN+'</div></td><td class="col-status">'+prodStatusBadge(p.status)+'</td><td class="col-act">'+actions+'</td></tr>'+
      '<tr class="sp-detail-row'+(exp?' open':'')+'" data-pid="'+p.id+'"><td colspan="6"><div class="sp-detail-wrap">'+
        '<div class="sp-detail-title">💸 成本 / 重量</div>'+prodCostWeightHtml(p)+
        '<div class="sp-detail-title" style="margin-top:10px">🔢 SKU 明细（'+skuN+'）</div>'+
        renderSkuDetailTable(p)+
      '</div></td></tr>';"""
assert old_row in src
src = src.replace(old_row, new_row)

# === 9) Version 65 → 66 ===
src = src.replace("var APP_VERSION=65;", "var APP_VERSION=66;", 1)

# === 10) 写入 ===
open(path, "w", encoding="utf-8").write(src)
print("V66 patch applied OK")
print("length:", len(src))
