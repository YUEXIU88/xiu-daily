# -*- coding: utf-8 -*-
path = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences\index.html"
src = open(path, "r", encoding="utf-8").read()

# === 1) saveData 优化 ===
old_save = "function saveData(key,val){try{localStorage.setItem(key,JSON.stringify(val));}catch(e){showToast('\\u5b58\\u50a8\\u7a7a\\u95f4\\u4e0d\\u8db3');}}"
new_save = "function saveData(key,val){try{var toSave=val;if(key===SK.spProducts&&Array.isArray(val)){toSave=val.map(function(p){var c={};for(var k in p){if(k!=='img')c[k]=p[k];}c.skus=(p.skus||[]).map(function(s){var cs={};for(var k2 in s){if(k2!=='img')cs[k2]=s[k2];}return cs;});return c;});}localStorage.setItem(key,JSON.stringify(toSave));}catch(e){console.warn('saveData failed:',key,e);showToast('\\u5b58\\u50a8\\u7a7a\\u95f4\\u4e0d\\u8db3');}}"
assert old_save in src, "saveData not found"
src = src.replace(old_save, new_save)

# === 2) renderSkuSiteCalc 替换 ===
marker_start = "function renderSkuSiteCalc(p,sk,si,sid){"
marker_end = "function renderProductPricePreview(p){"
idx_s = src.index(marker_start)
idx_e = src.index(marker_end)
old_func = src[idx_s:idx_e]
print("old_func length:", len(old_func))

new_func = (
    "function renderSkuSiteCalc(p,sk,si,sid){\n"
    "  var s=SHOPEE_SITES.find(function(x){return x.id===sid;});if(!s)return '';\n"
    "  var pr=(sk.price&&sk.price[s.id])||{};\n"
    "  var baseNum=parseFloat(pr.base)||0;\n"
    "  var disc=prodDisc(p,s.id);\n"
    "  var c=calcSkuSite(sk,s.id,disc);\n"
    "  var profCls=c.profit>=0?'pos':'neg';\n"
    "  var profSign=c.profit>=0?'+':'-';\n"
    "  if(baseNum<=0){\n"
    "    return '<span class=\"sp-pp-calc empty\"><span class=\"sp-pp-cny\">\u8f93\u5165\u539f\u4ef7\u8ba1\u7b97</span></span>';\n"
    "  }\n"
    "  var html='<span class=\"sp-pp-calc\" title=\"'+s.name+': \u539f\u4ef7 '+s.symbol+fmtNum(baseNum)+' \u2192 \u6298\u540e '+s.symbol+fmtNum(c.finalLocal)+' ('+disc+'%\u6298) \u2248\u00a5'+fmtNum(c.finalCny)+' \u5229\u6da6 \u00a5'+fmtNum(c.profit)+'\">';\n"
    "  html+='<span class=\"sp-pp-final\">\u6298\u540e '+s.symbol+fmtNum(c.finalLocal)+'</span>';\n"
    "  html+='<span class=\"sp-pp-cny\">\u2248\u00a5'+fmtNum(c.finalCny)+'</span>';\n"
    "  html+='<span class=\"sp-pp-profit '+profCls+'\">\u5229\u6da6 '+profSign+'\u00a5'+fmtNum(Math.abs(c.profit))+'</span>';\n"
    "  html+='</span>';\n"
    "  return html;\n"
    "}\n"
)
src = src[:idx_s] + new_func + src[idx_e:]

# === 3) CSS: 计算气泡新样式 ===
old_css = ".sp-pp-calc{display:inline-flex;align-items:center;gap:2px;margin-left:4px}"
new_css = (
    ".sp-pp-calc{display:inline-flex;align-items:center;gap:5px;margin-left:6px;padding:2px 6px;background:var(--card);border:1px solid var(--border-l);border-radius:8px;white-space:nowrap}\n"
    ".sp-pp-calc .sp-pp-final{font-size:12.5px;font-weight:700;color:var(--primary)}\n"
    ".sp-pp-calc .sp-pp-cny{font-size:11px;color:var(--text-3);font-weight:500}\n"
    ".sp-pp-calc .sp-pp-profit{display:inline-flex;align-items:center;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px}\n"
    ".sp-pp-calc .sp-pp-profit.pos{color:#1e7d34;background:#e6f7ec;border:1px solid #b5e0c2}\n"
    ".sp-pp-calc .sp-pp-profit.neg{color:#b22a2a;background:#fde8e8;border:1px solid #f4b4b4}\n"
    ".sp-pp-calc.empty{background:transparent;border:1px dashed var(--border-l);opacity:.7}\n"
    ".sp-pp-calc.empty .sp-pp-cny{font-style:italic;font-size:10.5px}"
)
assert old_css in src, "CSS not found"
src = src.replace(old_css, new_css)

# === 4) 修复 input handler ===
old_input_tail = "sk.price[sid][inp.dataset.key]=inp.value;saveData(SK.spProducts,spProducts);refreshSkuCalcCard(pid,si);var ppCalc=inp.parentElement&&inp.parentElement.querySelector('.sp-pp-calc');if(ppCalc){ppCalc.outerHTML=renderSkuSiteCalc(p,sk,si,sid);}var othInp=document.querySelector('input[data-sku-price=\"'+si+'\"][data-site=\"'+sid+'\"][data-key=\"'+inp.dataset.key+'\"]');if(othInp&&othInp!==inp&&document.activeElement!==othInp)othInp.value=inp.value;"

new_input_tail = "sk.price[sid][inp.dataset.key]=inp.value;var ppCell=inp.closest('.sp-pp-cell');var ppCalc=ppCell&&ppCell.nextElementSibling;if(ppCalc&&ppCalc.classList&&ppCalc.classList.contains('sp-pp-calc')){ppCalc.outerHTML=renderSkuSiteCalc(p,sk,si,sid);}if(window._spSaveTimer)clearTimeout(window._spSaveTimer);window._spSaveTimer=setTimeout(function(){saveData(SK.spProducts,spProducts);window._spSaveTimer=null;},150);var othInp=document.querySelector('input[data-sku-price=\"'+si+'\"][data-site=\"'+sid+'\"][data-key=\"'+inp.dataset.key+'\"]');if(othInp&&othInp!==inp&&document.activeElement!==othInp)othInp.value=inp.value;"

assert old_input_tail in src, "input handler tail not found"
src = src.replace(old_input_tail, new_input_tail)

# === 5) 折扣 handler 防抖 + 刷新主行计算气泡 ===
old_disc = "pp.disc[pd.dataset.prodDisc]=pd.value;saveData(SK.spProducts,spProducts);(pp.skus||[]).forEach(function(sk,si){refreshSkuCalcCard(ppid,si);});return;"

new_disc = (
    "pp.disc[pd.dataset.prodDisc]=pd.value;"
    "if(window._spDiscTimer)clearTimeout(window._spDiscTimer);"
    "window._spDiscTimer=setTimeout(function(){saveData(SK.spProducts,spProducts);window._spDiscTimer=null;},200);"
    "(pp.skus||[]).forEach(function(sk,si){"
    "var row=document.querySelector('tr[data-pid=\"'+ppid+'\"] .sp-pp-sku-line:nth-of-type('+(si+1)+')');"
    "if(row){var cells=row.querySelectorAll('.sp-pp-cell');"
    "cells.forEach(function(cell){var calc=cell.nextElementSibling;"
    "if(calc&&calc.classList&&calc.classList.contains('sp-pp-calc')){"
    "var sInp=cell.querySelector('input[data-sku-price]');"
    "if(sInp){var sIdx=parseInt(sInp.dataset.skuPrice);var sSite=sInp.dataset.site;"
    "calc.outerHTML=renderSkuSiteCalc(pp,pp.skus[sIdx],sIdx,sSite);}}});}"
    "refreshSkuCalcCard(ppid,si);});return;"
)
assert old_disc in src, "disc handler not found"
src = src.replace(old_disc, new_disc)

# === 6) pagehide 保护 ===
old_sync = "var _lastAutoSync=0;"
new_sync = (
    "var _lastAutoSync=0;"
    "window.addEventListener('pagehide',function(){"
    "if(window._spSaveTimer){clearTimeout(window._spSaveTimer);saveData(SK.spProducts,spProducts);}"
    "if(window._spDiscTimer){clearTimeout(window._spDiscTimer);saveData(SK.spProducts,spProducts);}"
    "});"
)
assert old_sync in src
src = src.replace(old_sync, new_sync)

# === 7) Version 66 -> 67 ===
src = src.replace("var APP_VERSION=66;", "var APP_VERSION=67;", 1)

open(path, "w", encoding="utf-8").write(src)
print("V67 patch applied OK, length:", len(src))
