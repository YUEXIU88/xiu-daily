"""
V76: SKU 行内单站点所有信息强制同一行
- 把 input cell (price+symbol) 和 calc (折后+人民币+利润) 用 .sp-pp-site-block 包裹
- site-block 内部 inline-flex + 不换行，flex-wrap 只在 SKU 之间
- 单站点高度压扁（去掉冗余边框）
"""
SRC='C:/Users/92809/WorkBuddy/2026-08-19-23-27-21/english-sentences/index.html'

with open(SRC,'r',encoding='utf-8') as f:
    src=f.read()

# 1) 重新组织 renderProductPricePreview：每个站点包 site-block
old = '''function renderProductPricePreview(p){
  var sites=calcSitesEnabled();
  if(!sites.length)return '';
  var skus=p.skus||[];
  if(!skus.length)return '';
  var lines=skus.map(function(sk,si){
    var skuLabel=sk.skuNo||sk.name||('SKU'+(si+1));
    var siteCells=sites.map(function(s){
      var calcHtml=renderSkuSiteCalc(p,sk,si,s.id);
      var pr=(sk.price&&sk.price[s.id])||{};
      var baseVal=pr.base!=null?String(pr.base):'';
      var inHtml='<span class="sp-pp-cell" onclick="event.stopPropagation()"><b>'+s.name+'</b> <input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-price="'+si+'" data-site="'+s.id+'" data-key="base" value="'+baseVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> '+s.symbol+'</span>';
      return inHtml+calcHtml;
    }).join('');
    var costVal=sk.cost!=null?String(sk.cost):'';
    var costHtml='<span class="sp-pp-cell sp-pp-cost-cell" onclick="event.stopPropagation()"><b>成本</b> <input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-cost="'+si+'" value="'+costVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> <span class="sp-pp-sku-cost-num">¥</span></span>';
    return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';
  }).join('');'''

new = '''function renderProductPricePreview(p){
  var sites=calcSitesEnabled();
  if(!sites.length)return '';
  var skus=p.skus||[];
  if(!skus.length)return '';
  var lines=skus.map(function(sk,si){
    var skuLabel=sk.skuNo||sk.name||('SKU'+(si+1));
    var siteCells=sites.map(function(s){
      var calcHtml=renderSkuSiteCalc(p,sk,si,s.id);
      var pr=(sk.price&&sk.price[s.id])||{};
      var baseVal=pr.base!=null?String(pr.base):'';
      var inHtml='<span class="sp-pp-cell" onclick="event.stopPropagation()"><b>'+s.name.charAt(0)+'</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-price="'+si+'" data-site="'+s.id+'" data-key="base" value="'+baseVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()"> '+s.symbol+'</span>';
      return '<span class="sp-pp-site-block" onclick="event.stopPropagation()">'+inHtml+calcHtml+'</span>';
    }).join('');
    var costVal=sk.cost!=null?String(sk.cost):'';
    var costHtml='<span class="sp-pp-site-block sp-pp-cost-block" onclick="event.stopPropagation()"><span class="sp-pp-cell sp-pp-cost-cell"><b>成本</b><input class="sp-pp-price-in" type="number" inputmode="decimal" step="0.01" min="0" data-sku-cost="'+si+'" value="'+costVal+'" placeholder="0" onclick="event.stopPropagation()" onfocus="event.stopPropagation()">¥</span></span>';
    return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';
  }).join('');'''

assert src.count(old)==1,'renderProductPricePreview 函数未匹配'
src=src.replace(old,new)

# 2) CSS: site-block 包裹样式 + 修正 sku-line 让其真正横向、only 在必要时 wrap
old_css='.sp-pp-sku-line{display:flex;align-items:center;gap:4px;flex-wrap:wrap;font-size:10.5px;line-height:1.6;width:100%}'
new_css='.sp-pp-sku-line{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:10.5px;line-height:1.6;width:100%}'
assert src.count(old_css)==1,'sp-pp-sku-line CSS 未匹配'
src=src.replace(old_css,new_css)

# 3) 新增 site-block 样式（含 cell/calc 内的内嵌布局）
old_css_marker='.sp-pp-date-line{display:flex;align-items:center;'
new_css_section='''.sp-pp-site-block{display:inline-flex;align-items:center;gap:5px;flex-shrink:0;background:var(--bg);border:1px solid var(--border-l);border-radius:8px;padding:2px 5px;white-space:nowrap;flex-wrap:nowrap}
.sp-pp-site-block>.sp-pp-cell{background:transparent;border:none;padding:1px 3px}
.sp-pp-site-block>.sp-pp-calc{margin-left:2px;padding:2px 7px;background:var(--card);border:1px solid var(--border);border-radius:7px}
.sp-pp-site-block.sp-pp-cost-block{background:#fff8e1;border-color:#ffb74d}
.sp-pp-date-line{display:flex;align-items:center;'''
assert src.count(old_css_marker)==1,'sp-pp-date-line CSS 未匹配'
src=src.replace(old_css_marker,new_css_section)

# 4) 限制 col-img 不需要那么宽了（220px 即可，新布局更紧凑）
old_w='.sp-prod-tbl .col-img{vertical-align:top;width:440px;padding-top:6px;padding-left:10px;padding-right:6px}'
new_w='.sp-prod-tbl .col-img{vertical-align:top;min-width:280px;max-width:480px;padding-top:6px;padding-left:10px;padding-right:6px}'
assert src.count(old_w)==1,'col-img width CSS 未匹配'
src=src.replace(old_w,new_w)

# 5) APP_VERSION 升 76
src=src.replace('var APP_VERSION=75;','var APP_VERSION=76;')

with open(SRC,'w',encoding='utf-8') as f:
    f.write(src)

print('V76 补丁完成')
print('已改动：')
print('  renderProductPricePreview: 每个站点包 site-block，单一 cell')
print('  CSS: .sp-pp-site-block inline-flex + cell/calc 内嵌')
print('  CSS: .sp-pp-sku-line gap 4→6 (小组间留呼吸)')
print('  CSS: .col-img width 440→min 280/max 480 (自适应)')
