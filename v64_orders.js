// ---------- Shopee: Orders (V64 重构: 25+ 字段, 核心列+折叠详情) ----------
function getSite(id){return SHOPEE_SITES.find(function(s){return s.id===id;})||SHOPEE_SITES[0];}
function allSkuOptions(){var opts=[];spProducts.forEach(function(p){(p.skus||[]).forEach(function(s){if(s.skuNo)opts.push({sku:s.skuNo,label:(fmtSkuNo(s.skuNo)+' · '+escapeHtml(p.title||p.name)+(s.name?' · '+escapeHtml(s.name):''))});});});return opts;}

// 订单派生计算（向后兼容旧 revenue/cost 字段）
function calcOrderDerived(o){
  var s=getSite(o.site);
  var rate=s.rate||1;
  var qty=o.qty||1;
  var unitPrice=o.unitPrice!=null?parseFloat(o.unitPrice)||0:(o.revenue?(parseFloat(o.revenue)||0)/qty:0);
  var unitCost=o.unitCost!=null?parseFloat(o.unitCost)||0:(o.cost?(parseFloat(o.cost)||0)/qty:0);
  var totalLocal=unitPrice*qty;
  var totalCny=totalLocal*rate;
  var coupon=parseFloat(o.coupon)||0;
  var orderAmountLocal=totalLocal-coupon;
  var orderAmountCny=orderAmountLocal*rate;
  var weight=parseFloat(o.actualWeight)||0;
  var hiddenFeeLocal=o.hiddenFee!=null?parseFloat(o.hiddenFee):(weight>0?s.shipping*weight/1000:0);
  var commissionLocal=orderAmountLocal*s.commission/100;
  var revenueLocal=orderAmountLocal-hiddenFeeLocal-commissionLocal;
  var revenueCny=revenueLocal*rate;
  var expressFee=parseFloat(o.expressFee)||0;
  var adCost=parseFloat(o.adCost)||0;
  var totalCost=unitCost*qty+expressFee+adCost;
  var profit=revenueCny-totalCost;
  var profitRate=revenueCny>0?(profit/revenueCny*100):0;
  var unitPriceCny=unitPrice*rate;
  return {s:s,rate:rate,qty:qty,unitPrice:unitPrice,unitCost:unitCost,totalLocal:totalLocal,totalCny:totalCny,coupon:coupon,orderAmountLocal:orderAmountLocal,orderAmountCny:orderAmountCny,hiddenFeeLocal:hiddenFeeLocal,hiddenFeeCny:hiddenFeeLocal*rate,commissionLocal:commissionLocal,commissionCny:commissionLocal*rate,revenueLocal:revenueLocal,revenueCny:revenueCny,expressFee:expressFee,adCost:adCost,totalCost:totalCost,profit:profit,profitRate:profitRate,unitPriceCny:unitPriceCny};
}

function fmtMonth(d){return (d||'').slice(0,7);}
function fmtTimeSlot(d){if(!d)return '';try{var t=new Date(d+'T00:00:00');var h=t.getHours();return h<6?'凌晨':h<12?'上午':h<18?'下午':'晚上';}catch(e){return '';}}

function renderOrdersTable(){
  var el=$('spOrdTable');if(!el)return;
  if(spOrders.length===0){el.innerHTML='<tbody><tr><td style="text-align:center;padding:40px;color:var(--text-3)">还没有订单，点击「＋ 添加订单」或「📥 批量导入」开始</td></tr></tbody>';return;}
  var head='<thead><tr><th>月份</th><th>日期</th><th>站点</th><th>订单号</th><th>产品</th><th>规格</th><th>数量</th><th>订单金额</th><th>利润(¥)</th><th>利润率</th><th>状态</th><th></th></tr></thead>';
  var body='<tbody>'+spOrders.map(function(o){
    var d=calcOrderDerived(o);
    var profitColor=d.profit>=0?'color:var(--success)':'color:var(--danger)';
    var profitRateStr=(d.profitRate>=0?'+':'')+d.profitRate.toFixed(1)+'%';
    var profitRateColor=d.profitRate>=0?'color:var(--success)':'color:var(--danger)';
    var row='<tr class="sp-ord-main" data-oid="'+o.id+'">'+
      '<td>'+fmtMonth(o.date)+'</td>'+
      '<td>'+fmtDate(o.date)+'</td>'+
      '<td>'+d.s.name+'</td>'+
      '<td>'+escapeHtml(o.orderId||'')+'</td>'+
      '<td>'+escapeHtml(o.product||'')+'</td>'+
      '<td class="sp-sku-no">'+(o.sku?escapeHtml(fmtSkuNo(o.sku)):'<span style="color:var(--text-3)">—</span>')+'</td>'+
      '<td class="num">'+d.qty+'</td>'+
      '<td class="num">'+d.s.symbol+fmtNum(d.orderAmountLocal)+'<br><span style="font-size:11px;color:var(--text-3)">¥'+fmtNum(d.orderAmountCny)+'</span></td>'+
      '<td class="num" style="'+profitColor+'"><b>¥'+fmtNum(d.profit)+'</b></td>'+
      '<td class="num" style="'+profitRateColor+'">'+profitRateStr+'</td>'+
      '<td>'+(o.status||'')+'</td>'+
      '<td><button class="act-btn" data-oexpand="'+o.id+'" title="展开/收起">▸</button><button class="act-btn" data-oedit="'+o.id+'">✏️</button><button class="act-btn danger" data-odel="'+o.id+'">🗑️</button></td>'+
      '</tr>';
    // detail row (hidden by default)
    row+='<tr class="sp-ord-detail" data-oid="'+o.id+'" style="display:none"><td colspan="12"><div class="sp-ord-detail-wrap">'+
      '<div class="sp-ord-detail-grid">'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">📅 时间</div><div class="sp-ord-dline">月份: '+fmtMonth(o.date)+'</div><div class="sp-ord-dline">日期: '+fmtDate(o.date)+'</div><div class="sp-ord-dline">时段: '+fmtTimeSlot(o.date)+'</div><div class="sp-ord-dline">发货日期: '+(o.shipDate?fmtDate(o.shipDate):'—')+'</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">🏷️ 标识</div><div class="sp-ord-dline">站点: '+d.s.name+'</div><div class="sp-ord-dline">订单号: '+escapeHtml(o.orderId||'')+'</div><div class="sp-ord-dline">二次销售: '+(o.resale==='yes'?'是':(o.resale==='no'?'否':'—'))+'</div><div class="sp-ord-dline">异常订单: '+(o.abnormal?escapeHtml(o.abnormal):'—')+'</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">📦 产品</div><div class="sp-ord-dline">产品名称: '+escapeHtml(o.product||'')+'</div><div class="sp-ord-dline">规格名称: '+(o.sku?escapeHtml(fmtSkuNo(o.sku)):'—')+'</div><div class="sp-ord-dline">数量: '+d.qty+'</div><div class="sp-ord-dline">实际发货数: '+(o.actualShipQty!=null?o.actualShipQty:d.qty)+'</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">💰 价格</div><div class="sp-ord-dline">单价: '+d.s.symbol+fmtNum(d.unitPrice)+' (¥'+fmtNum(d.unitPriceCny)+')</div><div class="sp-ord-dline">合计: '+d.s.symbol+fmtNum(d.totalLocal)+' (¥'+fmtNum(d.totalCny)+')</div><div class="sp-ord-dline">优惠券: '+d.s.symbol+fmtNum(d.coupon)+'</div><div class="sp-ord-dline">订单金额: '+d.s.symbol+fmtNum(d.orderAmountLocal)+' (¥'+fmtNum(d.orderAmountCny)+')</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">🚚 物流</div><div class="sp-ord-dline">实际重量: '+fmtNum(o.actualWeight||0)+'g</div><div class="sp-ord-dline">藏价: '+d.s.symbol+fmtNum(d.hiddenFeeLocal)+' (¥'+fmtNum(d.hiddenFeeCny)+')</div><div class="sp-ord-dline">佣金('+d.s.commission+'%): '+d.s.symbol+fmtNum(d.commissionLocal)+' (¥'+fmtNum(d.commissionCny)+')</div><div class="sp-ord-dline">订单收入: '+d.s.symbol+fmtNum(d.revenueLocal)+' (¥'+fmtNum(d.revenueCny)+')</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">💸 成本</div><div class="sp-ord-dline">单个成本: ¥'+fmtNum(d.unitCost)+'</div><div class="sp-ord-dline">总成本: ¥'+fmtNum(d.totalCost)+'</div><div class="sp-ord-dline">快递: '+escapeHtml(o.express||'—')+'</div><div class="sp-ord-dline">快递费: ¥'+fmtNum(d.expressFee)+'</div><div class="sp-ord-dline">广告: ¥'+fmtNum(d.adCost)+'</div></div>'+
        '<div class="sp-ord-dgroup"><div class="sp-ord-dtitle">📊 利润</div><div class="sp-ord-dline" style="'+profitColor+'">订单利润: ¥'+fmtNum(d.profit)+'</div><div class="sp-ord-dline" style="'+profitRateColor+'">利润率: '+profitRateStr+'</div><div class="sp-ord-dline">状态: '+(o.status||'')+'</div></div>'+
      '</div></div></td></tr>';
    return row;
  }).join('')+'</tbody>';
  el.innerHTML=head+body;
}

function showOrderForm(pid){
  editingDocId=pid||null;
  var old=pid?spOrders.find(function(x){return x.id===pid;}):null;
  var d=old?calcOrderDerived(old):null;
  var o=old?old:{date:todayStr(),site:'ph',orderId:'',product:'',sku:'',qty:1,unitPrice:'',unitCost:'',adCost:0,status:'待发货'};
  // backward compat: if old has revenue/cost but no unitPrice/unitCost, pre-fill from derived
  var initUnitPrice=o.unitPrice!=null?o.unitPrice:(d?d.unitPrice:'');
  var initUnitCost=o.unitCost!=null?o.unitCost:(d?d.unitCost:'');
  $('spOrdModalTitle').textContent=pid?'编辑订单':'添加订单';
  var popts=spProducts.map(function(p){return '<option value="'+escapeAttr(p.name)+'">';}).join('');
  var sopts=SHOPEE_SITES.map(function(s){return '<option value="'+s.id+'"'+(o.site===s.id?' selected':'')+'>'+s.name+' ('+s.currency+')</option>';}).join('');
  var skuOpts=allSkuOptions().map(function(x){return '<option value="'+escapeAttr(x.sku)+'">';}).join('');
  $('spOrdFormBody').innerHTML=
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">日期</label><input class="input" id="ofDate" type="date" value="'+escapeAttr(o.date||todayStr())+'"></div><div class="form-group" style="flex:1"><label class="form-label">站点</label><select class="input" id="ofSite">'+sopts+'</select></div><div class="form-group" style="flex:1"><label class="form-label">状态</label><select class="input" id="ofStatus"><option>待付款</option><option>待发货</option><option>已发货</option><option>已完成</option><option>已取消</option></select></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">订单号</label><input class="input" id="ofOrderId" value="'+escapeAttr(o.orderId||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">二次销售</label><select class="input" id="ofResale"><option value=""'+(o.resale===''||o.resale==null?' selected':'')+'>—</option><option value="no"'+(o.resale==='no'?' selected':'')+'>否</option><option value="yes"'+(o.resale==='yes'?' selected':'')+'>是</option></select></div><div class="form-group" style="flex:1"><label class="form-label">异常订单</label><input class="input" id="ofAbnormal" value="'+escapeAttr(o.abnormal||'')+'" placeholder="如: 退货/补发/缺货"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">产品名称</label><input class="input" id="ofProduct" list="ofProdList" value="'+escapeAttr(o.product||'')+'"><datalist id="ofProdList">'+popts+'</datalist></div><div class="form-group" style="flex:1"><label class="form-label">规格名称（SKU）</label><input class="input" id="ofSku" list="ofSkuList" value="'+escapeAttr(o.sku||'')+'"><datalist id="ofSkuList">'+skuOpts+'</datalist></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">数量</label><input class="input" id="ofQty" type="number" value="'+(o.qty||1)+'"></div><div class="form-group" style="flex:1"><label class="form-label">实际发货数</label><input class="input" id="ofActualQty" type="number" value="'+(o.actualShipQty!=null?o.actualShipQty:(o.qty||1))+'" placeholder="留空=数量"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">单价(本币)</label><input class="input" id="ofUnitPrice" type="number" step="0.01" value="'+initUnitPrice+'"></div><div class="form-group" style="flex:1"><label class="form-label">优惠券(本币)</label><input class="input" id="ofCoupon" type="number" step="0.01" value="'+(o.coupon||0)+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">实际重量(g)</label><input class="input" id="ofWeight" type="number" step="0.1" value="'+(o.actualWeight||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">藏价(本币·留空自动算)</label><input class="input" id="ofHiddenFee" type="number" step="0.01" value="'+(o.hiddenFee!=null?o.hiddenFee:'')+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">单个成本(¥)</label><input class="input" id="ofUnitCost" type="number" step="0.01" value="'+initUnitCost+'"></div><div class="form-group" style="flex:1"><label class="form-label">广告支出(¥)</label><input class="input" id="ofAd" type="number" step="0.01" value="'+(o.adCost||0)+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">发货日期</label><input class="input" id="ofShipDate" type="date" value="'+escapeAttr(o.shipDate||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">快递公司</label><input class="input" id="ofExpress" value="'+escapeAttr(o.express||'')+'" placeholder="如: SF/顺丰/4PX"></div><div class="form-group" style="flex:1"><label class="form-label">快递费(¥)</label><input class="input" id="ofExpressFee" type="number" step="0.01" value="'+(o.expressFee||0)+'"></div></div>'+
    '<div style="margin-top:8px;font-size:12px;color:var(--text-3)">💡 自动计算：合计=单价×数量 · 订单金额=合计-优惠券 · 佣金=订单金额×站点佣金率 · 订单收入=订单金额-藏价-佣金 · 总成本=单个成本×数量+快递费+广告 · 利润=订单收入(¥)-总成本 · 利润率=利润÷订单收入(¥)</div>';
  $('ofStatus').value=o.status||'待发货';
  var ofSku=$('ofSku');
  if(ofSku){
    ofSku.addEventListener('change',function(){
      var v=this.value;if(!v)return;
      for(var i=0;i<spProducts.length;i++){var p=spProducts[i];for(var j=0;j<(p.skus||[]).length;j++){var s=p.skus[j];if(s.skuNo===v){$('ofProduct').value=p.title||p.name;$('ofUnitCost').value=s.cost||'';$('ofWeight').value=s.weight||'';return;}}}
    });
  }
  $('spOrdModal').classList.add('open');$('spOrdModalMask').classList.add('open');
}

function saveOrder(){
  var o={
    date:$('ofDate').value,
    site:$('ofSite').value,
    orderId:$('ofOrderId').value.trim(),
    product:$('ofProduct').value.trim(),
    sku:$('ofSku').value.trim(),
    qty:parseInt($('ofQty').value)||1,
    actualShipQty:$('ofActualQty').value?parseInt($('ofActualQty').value):null,
    unitPrice:parseFloat($('ofUnitPrice').value)||0,
    coupon:parseFloat($('ofCoupon').value)||0,
    actualWeight:parseFloat($('ofWeight').value)||0,
    hiddenFee:$('ofHiddenFee').value?parseFloat($('ofHiddenFee').value):null,
    unitCost:parseFloat($('ofUnitCost').value)||0,
    adCost:parseFloat($('ofAd').value)||0,
    shipDate:$('ofShipDate').value,
    express:$('ofExpress').value.trim(),
    expressFee:parseFloat($('ofExpressFee').value)||0,
    status:$('ofStatus').value,
    resale:$('ofResale').value,
    abnormal:$('ofAbnormal').value.trim()
  };
  if(!o.product){showToast('请输入产品名');return;}
  if(editingDocId){var idx=spOrders.findIndex(function(x){return x.id===editingDocId;});if(idx>-1){o.id=editingDocId;spOrders[idx]=o;}}else{o.id=genId();spOrders.push(o);}
  saveData(SK.spOrders,spOrders);closeOrderForm();renderOrdersTable();showToast('已保存');
}

function closeOrderForm(){$('spOrdModal').classList.remove('open');$('spOrdModalMask').classList.remove('open');editingDocId=null;}

function importOrders(){
  var text=$('spOrdImportText').value;if(!text.trim()){showToast('请粘贴数据');return;}
  var rows=parseTable(text);var n=0;
  rows.forEach(function(r){if(r.length<4)return;var sku=(r[6]||'').trim();var skuInfo=null;if(sku){spProducts.forEach(function(p){(p.skus||[]).forEach(function(s){if(s.skuNo===sku)skuInfo={product:p.title||p.name,cost:s.cost};});});}var qty=parseInt(r[3])||1;var rev=parseFloat(r[4])||0;spOrders.push({id:genId(),date:(r[0]||todayStr()).trim(),site:'ph',orderId:(r[1]||'').trim(),product:skuInfo?skuInfo.product:(r[2]||'').trim(),sku:sku,qty:qty,unitPrice:rev/qty,unitCost:skuInfo?skuInfo.cost:(parseFloat(r[5])||0)/qty,adCost:0,status:'待发货'});n++;});
  saveData(SK.spOrders,spOrders);$('spOrdImportBox').style.display='none';$('spOrdImportText').value='';renderOrdersTable();showToast('已导入'+n+'条');
}

MODULES['sp-orders']={title:'订单管理',render:function(){
  return '<div class="section"><div class="toolbar"><button class="btn btn-primary" id="spAddOrdBtn">＋ 添加订单</button><button class="btn" id="spImportOrdBtn">📥 批量导入</button><button class="btn" id="spExportOrdBtn">📤 导出</button><input class="input" id="spOrdSearch" placeholder="🔍 搜索..." style="margin-left:auto;max-width:200px"></div><div class="table-wrap"><table class="data-table" id="spOrdTable"></table></div>'+
    '<div class="modal-mask" id="spOrdModalMask"></div><div class="modal" id="spOrdModal" style="max-width:680px"><div class="modal-title"><span id="spOrdModalTitle">添加订单</span><button class="modal-close" id="spOrdModalClose">✕</button></div><div id="spOrdFormBody"></div><div class="modal-actions"><button class="btn btn-primary" id="spSaveOrdBtn">保存</button><button class="btn" id="spCancelOrdBtn">取消</button></div></div>'+
    '<div class="import-dialog" id="spOrdImportBox" style="display:none"><div class="import-hint">粘贴订单数据。列：日期 / 订单号 / 产品 / 数量 / 售价 / 成本 / SKU号（可选）<br>填了 SKU 号会自动带出产品名与成本。</div><textarea id="spOrdImportText"></textarea><div class="modal-actions"><button class="btn btn-primary" id="spDoImportOrdBtn">导入</button><button class="btn" id="spCancelImportOrdBtn">取消</button></div></div></div>';
},init:function(){
  renderOrdersTable();
  $('spAddOrdBtn').addEventListener('click',function(){showOrderForm(null);});
  $('spImportOrdBtn').addEventListener('click',function(){$('spOrdImportBox').style.display='block';});
  $('spCancelImportOrdBtn').addEventListener('click',function(){$('spOrdImportBox').style.display='none';});
  $('spDoImportOrdBtn').addEventListener('click',importOrders);
  $('spExportOrdBtn').addEventListener('click',function(){var rows=[['月份','日期','时段','站点','订单号','二次销售','异常','产品','规格','数量','实际发货','单价(本币)','单价(¥)','合计(本币)','合计(¥)','优惠券','订单金额(本币)','订单金额(¥)','实际重量','藏价(本币)','藏价(¥)','佣金(本币)','佣金(¥)','订单收入(本币)','订单收入(¥)','单个成本','快递','快递费','广告','总成本','订单利润','利润率','状态','发货日期']];spOrders.forEach(function(o){var d=calcOrderDerived(o);rows.push([fmtMonth(o.date),fmtDate(o.date),fmtTimeSlot(o.date),d.s.name,o.orderId,o.resale==='yes'?'是':(o.resale==='no'?'否':''),o.abnormal||'',o.product,o.sku||'',d.qty,o.actualShipQty!=null?o.actualShipQty:d.qty,d.unitPrice.toFixed(2),d.unitPriceCny.toFixed(2),d.totalLocal.toFixed(2),d.totalCny.toFixed(2),d.coupon.toFixed(2),d.orderAmountLocal.toFixed(2),d.orderAmountCny.toFixed(2),o.actualWeight||0,d.hiddenFeeLocal.toFixed(2),d.hiddenFeeCny.toFixed(2),d.commissionLocal.toFixed(2),d.commissionCny.toFixed(2),d.revenueLocal.toFixed(2),d.revenueCny.toFixed(2),d.unitCost.toFixed(2),o.express||'',d.expressFee.toFixed(2),d.adCost.toFixed(2),d.totalCost.toFixed(2),d.profit.toFixed(2),d.profitRate.toFixed(1)+'%',o.status,o.shipDate||'']);});exportCSV('shopee订单.csv',rows);});
  $('spSaveOrdBtn').addEventListener('click',saveOrder);
  $('spCancelOrdBtn').addEventListener('click',closeOrderForm);
  $('spOrdModalClose').addEventListener('click',closeOrderForm);
  $('spOrdModalMask').addEventListener('click',closeOrderForm);
  $('spOrdSearch').addEventListener('input',renderOrdersTable);
  $('spOrdTable').addEventListener('click',function(e){
    var ex=e.target.closest('[data-oexpand]');var eb=e.target.closest('[data-oedit]');var db=e.target.closest('[data-odel]');
    if(ex){var id=ex.dataset.oexpand;var detail=document.querySelector('.sp-ord-detail[data-oid="'+id+'"]');if(detail){var open=detail.style.display!=='none';detail.style.display=open?'none':'table-row';ex.textContent=open?'▸':'▾';}}
    if(eb)showOrderForm(eb.dataset.oedit);
    if(db){if(confirm('删除该订单？')){spOrders=spOrders.filter(function(o){return o.id!==db.dataset.odel;});saveData(SK.spOrders,spOrders);renderOrdersTable();showToast('已删除');}}
  });
}};
