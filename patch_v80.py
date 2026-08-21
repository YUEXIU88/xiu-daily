# -*- coding: utf-8 -*-
"""
V80: SKU 行名称拆分 + 数量带单位
1. SKU 行：[产品名 chip] + [规格 chip]（去产品名前缀） + [数量 chip X个]
2. 兼容旧数据：若 sk.name 已包含产品名前缀，自动剥离开
3. CSS 新增 .sp-pp-prod-chip / .sp-pp-qty-chip
"""
import re

p = r"C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences\index.html"
with open(p, 'r', encoding='utf-8') as f:
    src = f.read()

orig = src

# ========== 1. renderProductPricePreview 重写 SKU 行 ==========
old_block = """  var lines=skus.map(function(sk,si){
    var skuLabel=sk.skuNo||sk.name||('SKU'+(si+1));
    var siteCells=sites.map(function(s){
      var calcHtml=renderSkuSiteCalc(p,sk,si,s.id);
      var pr=(sk.price&&sk.price[s.id])||{};
      var baseVal=pr.base!=null?String(pr.base):'';
      var inHtml='<span class="sp-pp-cell" onclick="event.stopPropagation()"><b>'+s.name.charAt(0)+'</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-price="'+si+'" data-site="'+s.id+'" data-key="base" value="'+baseVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> '+s.symbol+'</span>';
      return '<span class="sp-pp-site-block" onclick="event.stopPropagation()">'+inHtml+calcHtml+'</span>';
    }).join('');
    var costVal=sk.cost!=null?String(sk.cost):'';
    var costHtml='<span class="sp-pp-site-block sp-pp-cost-block" onclick="event.stopPropagation()"><span class="sp-pp-cell sp-pp-cost-cell"><b>\u6210\u672c</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-cost="'+si+'" value="'+costVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()">\u00a5</span></span>';
    return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';
  }).join('');"""

new_block = """  var lines=skus.map(function(sk,si){
    var skuLabel=sk.name||('\u89c4\u683c'+(si+1));
    var prodLabel=p.name||'';
    var displaySpec=skuLabel;
    if(prodLabel){
      var pn=prodLabel.trim();
      if(pn&&skuLabel.indexOf(pn)===0){
        var rest=skuLabel.slice(pn.length).replace(/^[\\-\\s\\.\\:]+/,'');
        if(rest)displaySpec=rest;
      }
    }
    var prodChip='<span class="sp-pp-prod-chip" title="'+escapeAttr(prodLabel||'')+'">'+escapeHtml(prodLabel||'\u4ea7\u54c1')+'</span>';
    var specChip='<span class="sp-pp-sku-name" title="'+escapeAttr(skuLabel)+'">'+escapeHtml(displaySpec)+'</span>';
    var qtyChip=(sk.qty&&parseInt(sk.qty)>0)?'<span class="sp-pp-qty-chip">'+parseInt(sk.qty)+'\u4e2a</span>':'';
    var siteCells=sites.map(function(s){
      var calcHtml=renderSkuSiteCalc(p,sk,si,s.id);
      var pr=(sk.price&&sk.price[s.id])||{};
      var baseVal=pr.base!=null?String(pr.base):'';
      var inHtml='<span class="sp-pp-cell" onclick="event.stopPropagation()"><b>'+s.name.charAt(0)+'</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-price="'+si+'" data-site="'+s.id+'" data-key="base" value="'+baseVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> '+s.symbol+'</span>';
      return '<span class="sp-pp-site-block" onclick="event.stopPropagation()">'+inHtml+calcHtml+'</span>';
    }).join('');
    var costVal=sk.cost!=null?String(sk.cost):'';
    var costHtml='<span class="sp-pp-site-block sp-pp-cost-block" onclick="event.stopPropagation()"><span class="sp-pp-cell sp-pp-cost-cell"><b>\u6210\u672c</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-cost="'+si+'" value="'+costVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()">\u00a5</span></span>';
    return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()">'+prodChip+specChip+qtyChip+costHtml+siteCells+'</div>';
  }).join('');"""

assert src.count(old_block) == 1, 'renderProductPricePreview block match=%d' % src.count(old_block)
src = src.replace(old_block, new_block)

# ========== 2. CSS: sp-pp-prod-chip + sp-pp-qty-chip ==========
old_css = '.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding-right:8px;border-right:1px dashed var(--border-l);margin-right:4px;white-space:nowrap;flex-shrink:0;min-width:100px;max-width:130px}'
new_css = '.sp-pp-prod-chip{display:inline-flex;align-items:center;font-size:10.5px;padding:1px 6px;background:var(--primary-l);color:var(--primary);border:1px solid var(--primary);border-radius:5px;margin-right:4px;font-weight:700;flex-shrink:0;max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:1.4}.sp-pp-prod-chip:empty{display:none}.sp-pp-sku-name{font-weight:600;color:var(--text);font-size:11.5px;line-height:1.4;display:inline-block;max-width:none;overflow-wrap:normal;padding:0 6px;border-right:1px dashed var(--border-l);margin-right:4px;white-space:nowrap;flex-shrink:0;min-width:80px;max-width:130px}.sp-pp-qty-chip{display:inline-flex;align-items:center;font-size:10.5px;padding:1px 6px;background:#fff3cd;color:#856404;border:1px solid #ffe69c;border-radius:5px;font-weight:700;flex-shrink:0;white-space:nowrap;line-height:1.4;margin-right:4px}'
assert src.count(old_css) == 1, 'sp-pp-sku-name CSS match=%d' % src.count(old_css)
src = src.replace(old_css, new_css)

# ========== 3. APP_VERSION 74 -> 80 ==========
src = src.replace('var APP_VERSION=79;', 'var APP_VERSION=80;', 1)

# ========== 4. 写入 ==========
with open(p, 'w', encoding='utf-8') as f:
    f.write(src)

import os
print('Patch V80 applied, file size:', os.path.getsize(p), 'bytes')
print('Diff:', len(src) - len(orig), 'bytes')
