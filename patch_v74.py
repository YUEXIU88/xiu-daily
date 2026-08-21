#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V74: Shopee SKU 行增加成本输入列 + 所有站点价格同左对齐到图片底"""
import re

src = open('index.html', 'r', encoding='utf-8').read()
orig_len = len(src)

# ========== 1) CSS: 增加成本单元格样式 ==========
old_css_marker = ".sp-pp-cell .sp-pp-final{color:var(--primary);font-weight:600}"
new_css = """.sp-pp-cell .sp-pp-final{color:var(--primary);font-weight:600}
.sp-pp-cost-cell{background:#fff8e1!important;border-color:#ffb74d!important}
.sp-pp-cost-cell input{font-weight:700;color:#b25e00;background:#fffbea}
.sp-pp-cost-cell input:focus{outline:2px solid #ff9800;border-color:#ff9800}
.sp-pp-sku-cost-num{font-size:9.5px;color:#b25e00;opacity:.75;margin-left:1px}"""
assert old_css_marker in src, "CSS marker not found"
src = src.replace(old_css_marker, new_css, 1)
print("1. CSS: OK")

# ========== 2) renderProductPricePreview: 在 SKU 号后插入成本输入 ==========
old_line = '''return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+siteCells+'</div>';'''
new_line = '''var costVal=sk.cost!=null?String(sk.cost):'';
    var costHtml='<span class="sp-pp-cell sp-pp-cost-cell" onclick="event.stopPropagation()"><b>成本</b> <input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-cost="'+si+'" value="'+costVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> <span class="sp-pp-sku-cost-num">¥</span></span>';
    return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';'''
assert old_line in src, "renderProductPricePreview line not found"
src = src.replace(old_line, new_line, 1)
print("2. renderProductPricePreview: OK")

# ========== 3) input handler: 增加 data-sku-cost 分支 ==========
old_inp_start = "var inp=e.target.closest('[data-sku-price]');if(!inp)return;"
new_inp_start = """var skuCostInp=e.target.closest('[data-sku-cost]');
  if(skuCostInp){
    var scRow=skuCostInp.closest('[data-pid]');if(!scRow)return;
    var scPid=scRow.dataset.pid;
    var scIdx=parseInt(skuCostInp.dataset.skuCost);if(isNaN(scIdx))return;
    var scP=spProducts.find(function(x){return x.id===scPid});
    if(!scP||!(scP.skus||[])[scIdx])return;
    scP.skus[scIdx].cost=skuCostInp.value;
    if(window._spCostTimer)clearTimeout(window._spCostTimer);
    window._spCostTimer=setTimeout(function(){saveData(SK.spProducts,spProducts);window._spCostTimer=null;},150);
    // 刷新该 SKU 行的所有站点计算气泡 + 同步展开区的卡片
    (scP.skus[scIdx] && [].slice.call(scRow.querySelectorAll('.sp-pp-sku-line'))).forEach=undefined;
    var scRowEl=document.querySelector('tr[data-pid="'+scPid+'"]');
    if(scRowEl){
      var skLine=scRowEl.querySelector('.sp-pp-sku-line:nth-of-type('+(scIdx+1)+')');
      if(skLine){
        var allCells=skLine.querySelectorAll('.sp-pp-calc');
        allCells.forEach(function(cEl){
          var prevCell=cEl.previousElementSibling;
          var prevInp=prevCell&&prevCell.querySelector('input[data-sku-price]');
          if(prevInp){
            var sIdx2=parseInt(prevInp.dataset.skuPrice);
            var sSite2=prevInp.dataset.site;
            cEl.outerHTML=renderSkuSiteCalc(scP,scP.skus[sIdx2],sIdx2,sSite2);
          }
        });
      }
    }
    refreshSkuCalcCard(scPid,scIdx);
    return;
  }
  var inp=e.target.closest('[data-sku-price]');if(!inp)return;"""
assert old_inp_start in src, "input handler start not found"
src = src.replace(old_inp_start, new_inp_start, 1)
print("3. input handler data-sku-cost: OK")

# ========== 4) 写回 ==========
open('index.html', 'w', encoding='utf-8').write(src)
print(f"\u603b\u6539\u52a8\u5b57\u8282: {len(src) - orig_len}")
print("V74 \u8865\u4e01\u6210\u529f\u3002")
