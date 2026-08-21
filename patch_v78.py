"""
V78: 折扣挪到 SKU 名后面（首个 SKU），序号变小 chip
"""
SRC='C:/Users/92809/WorkBuddy/2026-08-19-23-27-21/english-sentences/index.html'

with open(SRC,'r',encoding='utf-8') as f:
    src=f.read()

# 1) .sp-tb-idx 变小
old1='.sp-tb-idx{font-size:11px;color:var(--text-2);font-weight:700;text-align:center;margin-bottom:4px;background:var(--primary-l);color:var(--primary);border-radius:10px;padding:1px 0;letter-spacing:.5px}'
new1='.sp-tb-idx{font-size:10px;font-weight:700;background:var(--primary-l);color:var(--primary);border-radius:8px;padding:1px 7px;display:inline-block;width:fit-content;margin:0 0 4px 0;letter-spacing:.3px}'
assert src.count(old1)==1,'sp-tb-idx CSS 未匹配'
src=src.replace(old1,new1)

# 2) renderProductGrid：删除 col-img 内部的 prodDiscInputs 调用
old2=r"""<td class="col-img">'+img+prodDiscInputs(p)+renderProductPricePreview(p)+'</td>"""
new2=r"""<td class="col-img">'+img+renderProductPricePreview(p)+'</td>"""
assert src.count(old2)==1,'col-img 拼接 未匹配'
src=src.replace(old2,new2)

# 3) renderProductPricePreview 头部插入 discInline + isFirst
old3=r"""function renderProductPricePreview(p){
  var sites=calcSitesEnabled();
  if(!sites.length)return '';
  var skus=p.skus||[];
  if(!skus.length)return '';
  var lines=skus.map(function(sk,si){"""
new3=r"""function renderProductPricePreview(p){
  var sites=calcSitesEnabled();
  if(!sites.length)return '';
  var skus=p.skus||[];
  if(!skus.length)return '';
  // 产品级折扣 mini（仅在首个 SKU 名后显示一次）
  var discInline=sites.map(function(s){
    var dv=(p.disc&&p.disc[s.id]!=null&&p.disc[s.id]!=="")?p.disc[s.id]:prodDisc(p,s.id);
    return '<span class="sp-pp-disc-mini" onclick="event.stopPropagation()"><b>'+s.name.charAt(0)+'</b><input class="sp-disc-prod-in sp-disc-mini-in" data-prod-disc="'+s.id+'" type="number" step="0.1" min="0" value="'+dv+'" onclick="this.select()" placeholder="0">%</span>';
  }).join('');
  var discHtml='<span class="sp-pp-disc-inline" onclick="event.stopPropagation()">'+discInline+'</span>';
  var lines=skus.map(function(sk,si){
    var isFirst=si===0;"""
assert src.count(old3)==1,'renderProductPricePreview 头部 未匹配'
src=src.replace(old3,new3)

# 4) sku-line 末尾插入 isFirst 判断
old4=r"""return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';"""
new4=r"""return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+(isFirst?discHtml:"")+costHtml+siteCells+'</div>';"""
assert src.count(old4)==1,'sku-line 拼接 未匹配'
src=src.replace(old4,new4)

# 5) 新增 .sp-pp-disc-mini 紧凑样式
old5='.sp-pp-site-block{display:inline-flex'
new5='''.sp-pp-disc-inline{display:inline-flex;align-items:center;gap:4px;flex-shrink:0}
.sp-pp-disc-mini{display:inline-flex;align-items:center;gap:2px;padding:1px 4px 1px 6px;border-radius:5px;background:var(--bg);border:1px solid var(--border-l);font-size:10px;white-space:nowrap;height:18px}
.sp-pp-disc-mini b{color:var(--text-3);font-weight:600;font-size:10px;margin-right:2px}
.sp-pp-disc-mini input{width:32px;font-size:11px;border:none;background:transparent;text-align:right;color:var(--primary);font-weight:700;padding:0 2px;font-family:inherit;height:16px;outline:none}
.sp-pp-disc-mini input:focus{background:#fff;color:var(--primary-d);box-shadow:inset 0 0 0 1px var(--primary);border-radius:3px}
.sp-pp-disc-mini::after{content:"%";color:var(--text-3);font-size:10px;margin-left:1px}
.sp-pp-site-block{display:inline-flex'''
assert src.count(old5)==1,'sp-pp-site-block CSS 未匹配'
src=src.replace(old5,new5)

# 6) APP_VERSION 升 78
src=src.replace('var APP_VERSION=77;','var APP_VERSION=78;')

with open(SRC,'w',encoding='utf-8') as f:
    f.write(src)

print('V78 补丁完成')
print('  序号: .sp-tb-idx 小 chip (inline-block fit-content 10px)')
print('  折扣: 从 col-img 顶部删除，移动到首个 SKU 名后面')
