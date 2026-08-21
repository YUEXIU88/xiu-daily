# -*- coding: utf-8 -*-
# V81: 1) SKU号统一为「标题-规格-数量个」规则（豆浆过滤网 #100目-15x20-1个）
#      2) 利润气泡显示费用明细（藏价/佣金/优惠券/成本/其它/广告），利润=实付-全部费用
import io, re

path = 'index.html'
src = io.open(path, 'r', encoding='utf-8').read()
orig_len = len(src)

def rep(old, new, tag, count=1):
    global src
    n = src.count(old)
    assert n == count, '[%s] match=%d expect=%d' % (tag, n, count)
    src = src.replace(old, new)
    print('OK [%s]' % tag)

# ============ 1. genSkuNoFrom：保留 # 格式，生成「标题-规格-数量个」 ============
old = r'''function genSkuNoFrom(prodName,skuName,qty){var clean=function(s){return(s||'').trim().replace(/[^\w\u4e00-\u9fa5]+/g,'-').replace(/^-|-$/g,'').substring(0,20);};return clean(prodName)+'-'+clean(skuName)+'-'+(parseInt(qty)||1)+'个';}'''
new = r'''function genSkuNoFrom(prodName,skuName,qty){var clean=function(s){s=(s||'').trim().replace(/\s+/g,' ').replace(/\s*#\s*/g,' #');s=s.replace(/[^\w\u4e00-\u9fa5# ]+/g,'-').replace(/-{2,}/g,'-').replace(/^-|-$/g,'');return s.substring(0,30);};return clean(prodName)+'-'+clean(skuName)+'-'+(parseInt(qty)||1)+'个';}
// V81: SKU 号显示规则 = 标题(含#变体) + '-' + 规格(剥离产品名/变体前缀) + '-' + 数量个
function buildSkuNoLabel(p,sk,si){
  var skuLabel=(sk.name||'').trim()||('\u89c4\u683c'+(si+1));
  var prodLabel=(p.title||p.name||'').trim();
  if(!prodLabel)return skuLabel;
  var rest=skuLabel;
  if(rest.indexOf(prodLabel)===0){rest=rest.slice(prodLabel.length);}
  else{
    var hi=prodLabel.indexOf('#');
    var base=hi>-1?prodLabel.slice(0,hi).trim():prodLabel;
    if(base&&rest.indexOf(base)===0)rest=rest.slice(base.length);
    if(hi>-1){var vari=prodLabel.slice(hi+1).trim();if(vari&&rest.replace(/^[\-\s\.\:]+/,'').indexOf(vari)===0)rest=rest.replace(/^[\-\s\.\:]+/,'').slice(vari.length);}
  }
  rest=rest.replace(/^[\-\s\.\:]+/,'').replace(/[\-\s]+$/,'');
  var label=prodLabel;
  if(rest)label+='-'+rest;
  var q=parseInt(sk.qty)||0;
  if(q>0)label+='-'+q+'\u4e2a';
  return label;
}'''
rep(old, new, 'genSkuNoFrom + buildSkuNoLabel')

# ============ 2. renderProductPricePreview：三个chip合并为单一SKU号chip ============
old = r'''    var skuLabel=sk.name||('规格'+(si+1));
    var prodLabel=p.name||'';
    var displaySpec=skuLabel;
    if(prodLabel){
      var pn=prodLabel.trim();
      if(pn&&skuLabel.indexOf(pn)===0){
        var rest=skuLabel.slice(pn.length).replace(/^[\-\s\.\:]+/,'');
        if(rest)displaySpec=rest;
      }
    }
    var prodChip='<span class="sp-pp-prod-chip" title="'+escapeAttr(prodLabel||'')+'">'+escapeHtml(prodLabel||'产品')+'</span>';
    var specChip='<span class="sp-pp-sku-name" title="'+escapeAttr(skuLabel)+'">'+escapeHtml(displaySpec)+'</span>';
    var qtyChip=(sk.qty&&parseInt(sk.qty)>0)?'<span class="sp-pp-qty-chip">'+parseInt(sk.qty)+'个</span>':'';'''
new = r'''    var skuNoLabel=buildSkuNoLabel(p,sk,si);
    var skuNoChip='<span class="sp-pp-skuno-chip" title="'+escapeAttr(skuNoLabel)+'">'+escapeHtml(skuNoLabel)+'</span>';'''
rep(old, new, 'SKU chips -> single skuNo chip')

old = r'''return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()">'+prodChip+specChip+qtyChip+costHtml+siteCells+'</div>';'''
new = r'''return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()">'+skuNoChip+costHtml+siteCells+'</div>';'''
rep(old, new, 'sku-line html')

# ============ 3. CSS：新增 .sp-pp-skuno-chip ============
old = '.sp-pp-prod-chip{display:inline-flex;align-items:center;font-size:10.5px;padding:1px 6px;background:var(--primary-l);color:var(--primary);border:1px solid var(--primary);border-radius:5px;margin-right:4px;font-weight:700;flex-shrink:0;max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:1.4}.sp-pp-prod-chip:empty{display:none}'
new = old + '.sp-pp-skuno-chip{display:inline-flex;align-items:center;font-size:11px;padding:1px 8px;background:var(--primary-l);color:var(--primary);border:1px solid var(--primary);border-radius:6px;margin-right:6px;font-weight:700;flex-shrink:0;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:1.5}'
rep(old, new, 'CSS skuno-chip')

# ============ 4. renderSkuSiteCalc：利润气泡加费用明细 ============
old = r'''  var html='<span class="sp-pp-calc" title="'+s.name+': 原价 '+s.symbol+fmtNum(baseNum)+' → 折后 '+s.symbol+fmtNum(c.finalLocal)+' ('+disc+'%折) ≈¥'+fmtNum(c.finalCny)+' 利润 ¥'+fmtNum(c.profit)+'">';
  html+='<span class="sp-pp-final">'+s.symbol+fmtNum(c.finalLocal)+'</span>';
  html+='<span class="sp-pp-cny">≈¥'+fmtNum(c.finalCny)+'</span>';
  html+='<span class="sp-pp-profit '+profCls+'">'+profSign+'¥'+fmtNum(Math.abs(c.profit))+'</span>';'''
new = r'''  var fees=c.hideCny+c.commCny+c.cost+c.other+c.ad;
  var feeTip='费用明细（已全部从利润中扣除）：藏价 ¥'+fmtNum(c.hideCny)+' + 佣金('+fmtNum(c.commission)+'%) ¥'+fmtNum(c.commCny)+' + 成本 ¥'+fmtNum(c.cost)+' + 优惠券 ¥'+fmtNum(c.coupon*c.rate)+' + 其它 ¥'+fmtNum(c.other)+' + 广告 ¥'+fmtNum(c.ad)+' = 合计 ¥'+fmtNum(fees);
  var html='<span class="sp-pp-calc" title="'+s.name+': 原价 '+s.symbol+fmtNum(baseNum)+' → 折后 '+s.symbol+fmtNum(c.finalLocal)+' ('+disc+'%折) ≈¥'+fmtNum(c.finalCny)+'&#10;'+feeTip+'&#10;利润 = 实付 ¥'+fmtNum(c.finalCny)+' - 费用 ¥'+fmtNum(fees)+' = ¥'+fmtNum(c.profit)+'">';
  html+='<span class="sp-pp-final">'+s.symbol+fmtNum(c.finalLocal)+'</span>';
  html+='<span class="sp-pp-cny">≈¥'+fmtNum(c.finalCny)+'</span>';
  html+='<span class="sp-pp-fees" title="'+escapeAttr(feeTip)+'">-费¥'+fmtNum(fees)+'</span>';
  html+='<span class="sp-pp-profit '+profCls+'" title="净利 = 实付 - 全部费用">'+profSign+'¥'+fmtNum(Math.abs(c.profit))+'</span>';'''
rep(old, new, 'calc bubble fees')

# ============ 5. CSS：.sp-pp-fees 样式 ============
old = '.sp-pp-calc .sp-pp-cny{font-size:11px;color:var(--text-3);font-weight:500}'
new = old + '.sp-pp-calc .sp-pp-fees{font-size:10px;color:var(--text-3);font-weight:600;background:var(--bg);padding:1px 5px;border-radius:8px;cursor:help}'
rep(old, new, 'CSS fees chip')

# ============ 6. saveProduct / renderSkuInputs / importProducts：SKU号用标题生成 ============
old = r'''if(!sk.skuNo)sk.skuNo=genSkuNoFrom(name,sk.name,sk.qty);'''
new = r'''if(!sk.skuNo)sk.skuNo=genSkuNoFrom(p.title||name,sk.name,sk.qty);'''
rep(old, new, 'saveProduct genSkuNo')

old = r'''var html=skus.map(function(s){var suggested=s.skuNo||'';if(!suggested&&prodName&&s.name)suggested=genSkuNoFrom(prodName,s.name,s.qty);'''
new = r'''var prodTitle=($('pfTitle')?$('pfTitle').value.trim():'')||prodName;var html=skus.map(function(s){var suggested=s.skuNo||'';if(!suggested&&prodTitle&&s.name)suggested=genSkuNoFrom(prodTitle,s.name,s.qty);'''
rep(old, new, 'renderSkuInputs genSkuNo')

old = r'''skus.push({skuNo:genSkuNoFrom(name,skuName,skuQty),name:skuName,enName:skuEnName,qty:skuQty,cost:cost,weight:weight});'''
new = r'''skus.push({skuNo:genSkuNoFrom(title||name,skuName,skuQty),name:skuName,enName:skuEnName,qty:skuQty,cost:cost,weight:weight});'''
rep(old, new, 'importProducts genSkuNo')

# ============ 7. 版本号 ============
old = 'var APP_VERSION=80;'
new = 'var APP_VERSION=81;'
rep(old, new, 'APP_VERSION')

io.open(path, 'w', encoding='utf-8').write(src)
print('Total: +%d bytes' % (len(src) - orig_len))
