// ==================== V64 NEW MODULES: Purchase / Stock / Ads ====================
// Injected before MODULES['sp-stats']

// ---------- Shopee: Purchase (采购表) ----------
function renderPurchaseTable(){
  var el=$('spPurTable');if(!el)return;
  var q='';var si=$('spPurSearch');if(si)q=si.value.toLowerCase();
  var list=spPurchase.filter(function(r){return !q||(r.skuName||'').toLowerCase().indexOf(q)!==-1||(r.poNo||'').toLowerCase().indexOf(q)!==-1||(r.supplier||'').toLowerCase().indexOf(q)!==-1;});
  if(list.length===0){el.innerHTML='<tbody><tr><td style="text-align:center;padding:40px;color:var(--text-3)">还没有采购记录，点击「＋ 添加采购」开始</td></tr></tbody>';return;}
  var head='<thead><tr><th>月份</th><th>下单日期</th><th>单号</th><th>规格名称</th><th>数量</th><th>单价</th><th>合计</th><th>国内运费</th><th>总金额</th><th>实际支付</th><th>分摊运费</th><th>含运单价</th><th>供应商</th><th>备注</th><th></th></tr></thead>';
  var body='<tbody>'+list.map(function(r){
    var total=(r.qty||0)*(r.unitPrice||0);
    var totalAmount=total+(r.domesticShip||0);
    var actualPay=r.actualPay||totalAmount;
    var unitWithShip=r.qty>0?(actualPay/r.qty):0;
    var sharedShip=unitWithShip-(r.unitPrice||0);
    return '<tr><td>'+(r.month||'')+'</td><td>'+fmtDate(r.orderDate)+'</td><td>'+escapeHtml(r.poNo||'')+'</td><td>'+escapeHtml(r.skuName||'')+'</td><td class="num">'+(r.qty||0)+'</td><td class="num">¥'+fmtNum(r.unitPrice)+'</td><td class="num">¥'+fmtNum(total)+'</td><td class="num">¥'+fmtNum(r.domesticShip||0)+'</td><td class="num">¥'+fmtNum(totalAmount)+'</td><td class="num">¥'+fmtNum(actualPay)+'</td><td class="num">¥'+fmtNum(sharedShip)+'</td><td class="num">¥'+fmtNum(unitWithShip)+'</td><td>'+escapeHtml(r.supplier||'')+'</td><td>'+escapeHtml(r.remark||'')+'</td><td><button class="act-btn" data-pur-edit="'+r.id+'">✏️</button><button class="act-btn danger" data-pur-del="'+r.id+'">🗑️</button></td></tr>';
  }).join('')+'</tbody>';
  var totalPay=list.reduce(function(s,r){return s+(r.actualPay||((r.qty||0)*(r.unitPrice||0)+(r.domesticShip||0)));},0);
  body+='<tfoot><tr style="font-weight:bold;background:var(--bg-2)"><td colspan="9">合计</td><td class="num">¥'+fmtNum(totalPay)+'</td><td colspan="4"></td><td></td></tr></tfoot>';
  el.innerHTML=head+body;
}

function showPurchaseForm(pid){
  editingDocId=pid||null;
  var r=pid?spPurchase.find(function(x){return x.id===pid;}):{month:todayStr().slice(0,7),orderDate:todayStr(),poNo:'',skuName:'',qty:1,unitPrice:'',domesticShip:0,actualPay:'',supplier:'',remark:''};
  $('spPurModalTitle').textContent=pid?'编辑采购':'添加采购';
  var skuOpts=allSkuOptions().map(function(x){return '<option value="'+escapeAttr(x.sku)+'">';}).join('');
  $('spPurFormBody').innerHTML=
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">月份</label><input class="input" id="purMonth" type="month" value="'+escapeAttr(r.month||todayStr().slice(0,7))+'"></div><div class="form-group" style="flex:1"><label class="form-label">下单日期</label><input class="input" id="purDate" type="date" value="'+escapeAttr(r.orderDate||todayStr())+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">单号</label><input class="input" id="purNo" value="'+escapeAttr(r.poNo||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">规格名称（SKU）</label><input class="input" id="purSku" list="purSkuList" value="'+escapeAttr(r.skuName||'')+'"><datalist id="purSkuList">'+skuOpts+'</datalist></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">数量</label><input class="input" id="purQty" type="number" value="'+(r.qty||1)+'"></div><div class="form-group" style="flex:1"><label class="form-label">单价(¥)</label><input class="input" id="purPrice" type="number" step="0.01" value="'+(r.unitPrice||'')+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">国内运费(¥)</label><input class="input" id="purShip" type="number" step="0.01" value="'+(r.domesticShip||0)+'"></div><div class="form-group" style="flex:1"><label class="form-label">实际支付(¥)</label><input class="input" id="purPay" type="number" step="0.01" value="'+(r.actualPay||'')+'" placeholder="留空则自动=合计+运费"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">供应商</label><input class="input" id="purSupplier" value="'+escapeAttr(r.supplier||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">备注</label><input class="input" id="purRemark" value="'+escapeAttr(r.remark||'')+'"></div></div>'+
    '<div style="margin-top:8px;font-size:12px;color:var(--text-3)">💡 合计=数量×单价，总金额=合计+国内运费，含运单价=实际支付÷数量，分摊运费=含运单价-单价。实际支付留空时自动=总金额。</div>';
  $('spPurModal').classList.add('open');$('spPurModalMask').classList.add('open');
}

function closePurchaseForm(){$('spPurModal').classList.remove('open');$('spPurModalMask').classList.remove('open');editingDocId=null;}

function savePurchase(){
  var id=editingDocId||genId();
  var qty=parseInt($('purQty').value)||0;
  var price=parseFloat($('purPrice').value)||0;
  var ship=parseFloat($('purShip').value)||0;
  var payStr=$('purPay').value.trim();
  var total=qty*price;
  var totalAmount=total+ship;
  var actualPay=payStr?parseFloat(payStr):totalAmount;
  var r={id:id,month:$('purMonth').value,orderDate:$('purDate').value,poNo:$('purNo').value.trim(),skuName:$('purSku').value.trim(),qty:qty,unitPrice:price,domesticShip:ship,actualPay:actualPay,supplier:$('purSupplier').value.trim(),remark:$('purRemark').value.trim()};
  if(!r.skuName){showToast('请填写规格名称');return;}
  if(editingDocId){var idx=spPurchase.findIndex(function(x){return x.id===id;});if(idx>=0)spPurchase[idx]=r;else spPurchase.push(r);}else spPurchase.push(r);
  saveData(SK.spPurchase,spPurchase);
  closePurchaseForm();
  renderPurchaseTable();
  showToast('已保存');
}

MODULES['sp-purchase']={title:'采购表',render:function(){
  return '<div class="section"><div class="toolbar"><button class="btn btn-primary" id="spAddPurBtn">＋ 添加采购</button><button class="btn" id="spExportPurBtn">📤 导出</button><input class="input" id="spPurSearch" placeholder="🔍 搜索..." style="margin-left:auto;max-width:200px"></div><div class="table-wrap"><table class="data-table" id="spPurTable"></table></div>'+
    '<div class="modal-mask" id="spPurModalMask"></div><div class="modal" id="spPurModal"><div class="modal-title"><span id="spPurModalTitle">添加采购</span><button class="modal-close" id="spPurModalClose">✕</button></div><div id="spPurFormBody"></div><div class="modal-actions"><button class="btn btn-primary" id="spSavePurBtn">保存</button><button class="btn" id="spCancelPurBtn">取消</button></div></div></div>';
},init:function(){
  renderPurchaseTable();
  $('spAddPurBtn').addEventListener('click',function(){showPurchaseForm(null);});
  $('spSavePurBtn').addEventListener('click',savePurchase);
  $('spCancelPurBtn').addEventListener('click',closePurchaseForm);
  $('spPurModalClose').addEventListener('click',closePurchaseForm);
  $('spPurModalMask').addEventListener('click',closePurchaseForm);
  $('spPurSearch').addEventListener('input',renderPurchaseTable);
  $('spExportPurBtn').addEventListener('click',function(){var rows=[['月份','下单日期','单号','规格名称','数量','单价','合计','国内运费','总金额','实际支付','分摊运费','含运单价','供应商','备注']];spPurchase.forEach(function(r){var total=(r.qty||0)*(r.unitPrice||0);var totalAmount=total+(r.domesticShip||0);var actualPay=r.actualPay||totalAmount;var unitWithShip=r.qty>0?(actualPay/r.qty):0;var sharedShip=unitWithShip-(r.unitPrice||0);rows.push([r.month,fmtDate(r.orderDate),r.poNo,r.skuName,r.qty,r.unitPrice,total.toFixed(2),r.domesticShip||0,totalAmount.toFixed(2),actualPay.toFixed(2),sharedShip.toFixed(2),unitWithShip.toFixed(2),r.supplier,r.remark]);});exportCSV('shopee采购.csv',rows);});
  $('spPurTable').addEventListener('click',function(e){
    var eb=e.target.closest('[data-pur-edit]');var db=e.target.closest('[data-pur-del]');
    if(eb)showPurchaseForm(eb.dataset.purEdit);
    if(db){if(confirm('删除该采购记录？')){spPurchase=spPurchase.filter(function(x){return x.id!==db.dataset.purDel;});saveData(SK.spPurchase,spPurchase);renderPurchaseTable();showToast('已删除');}}
  });
}};

// ---------- Shopee: Stock (库存表 - 自动汇总) ----------
function buildStockRows(){
  var map={};
  // 1. from purchase: sum qty and amount by skuName
  spPurchase.forEach(function(r){
    var k=r.skuName||'';if(!k)return;
    if(!map[k])map[k]={skuName:k,productName:'',totalPurCount:0,totalPurQty:0,totalPurAmount:0,soldQty:0};
    map[k].totalPurCount++;
    map[k].totalPurQty+=(r.qty||0);
    map[k].totalPurAmount+=(r.actualPay||((r.qty||0)*(r.unitPrice||0)+(r.domesticShip||0)));
  });
  // 2. from orders: sum sold qty by sku (sku is skuNo in orders)
  spOrders.forEach(function(o){
    var k=o.sku||'';if(!k)return;
    if(!map[k])map[k]={skuName:k,productName:'',totalPurCount:0,totalPurQty:0,totalPurAmount:0,soldQty:0};
    map[k].soldQty=(map[k].soldQty||0)+(o.qty||0);
  });
  // 3. product name from spProducts
  spProducts.forEach(function(p){
    (p.skus||[]).forEach(function(s){
      var k=s.skuNo||'';
      if(k&&map[k]&&!map[k].productName){map[k].productName=p.title||p.name;}
    });
  });
  // 4. compute derived fields with manual adjust
  var rows=Object.keys(map).map(function(k){
    var r=map[k];
    r.manualAdjust=spStockManual[k]||0;
    r.totalSold=(r.soldQty||0)+r.manualAdjust;
    r.currentStock=r.totalPurQty-r.totalSold;
    r.avgUnitPrice=r.totalPurQty>0?r.totalPurAmount/r.totalPurQty:0;
    r.stockCost=r.currentStock*r.avgUnitPrice;
    return r;
  });
  rows.sort(function(a,b){return b.stockCost-a.stockCost;});
  return rows;
}

function renderStockTable(){
  var el=$('spStockTable');if(!el)return;
  var rows=buildStockRows();
  if(rows.length===0){el.innerHTML='<tbody><tr><td style="text-align:center;padding:40px;color:var(--text-3)">还没有库存数据，请先在「采购表」中添加采购记录</td></tr></tbody>';return;}
  var head='<thead><tr><th>规格名称</th><th>产品名称</th><th>总采购(次)</th><th>总采购数量</th><th>销量</th><th>手动加减</th><th>合计销量</th><th>现库存</th><th>平均单价</th><th>库存成本</th></tr></thead>';
  var body='<tbody>'+rows.map(function(r){
    var stockColor=r.currentStock<0?'color:var(--danger)':(r.currentStock<10?'color:var(--warning)':'color:var(--success)');
    return '<tr><td>'+escapeHtml(r.skuName)+'</td><td>'+escapeHtml(r.productName||'—')+'</td><td class="num">'+r.totalPurCount+'</td><td class="num">'+r.totalPurQty+'</td><td class="num">'+(r.soldQty||0)+'</td><td class="num"><input type="number" class="stock-manual-input" data-sku="'+escapeAttr(r.skuName)+'" value="'+r.manualAdjust+'" style="width:60px;text-align:right" title="正数=增加销量(扣减库存)，负数=减少销量(增加库存)"></td><td class="num">'+r.totalSold+'</td><td class="num" style="'+stockColor+'"><b>'+r.currentStock+'</b></td><td class="num">¥'+fmtNum(r.avgUnitPrice)+'</td><td class="num">¥'+fmtNum(r.stockCost)+'</td></tr>';
  }).join('')+'</tbody>';
  var totalStock=rows.reduce(function(s,r){return s+r.stockCost;},0);
  var totalQty=rows.reduce(function(s,r){return s+r.currentStock;},0);
  body+='<tfoot><tr style="font-weight:bold;background:var(--bg-2)"><td colspan="7">合计</td><td class="num">'+totalQty+'</td><td></td><td class="num">¥'+fmtNum(totalStock)+'</td></tr></tfoot>';
  el.innerHTML=head+body;
}

MODULES['sp-stock']={title:'库存表',render:function(){
  return '<div class="section"><div class="toolbar"><button class="btn" id="spStockRefreshBtn">🔄 刷新</button><button class="btn" id="spExportStockBtn">📤 导出</button><span style="margin-left:auto;font-size:13px;color:var(--text-3)">💡 库存从「采购表」和「订单管理」自动汇总，手动加减用于纠偏/盘点</span></div><div class="table-wrap"><table class="data-table" id="spStockTable"></table></div></div>';
},init:function(){
  renderStockTable();
  $('spStockRefreshBtn').addEventListener('click',function(){renderStockTable();showToast('已刷新');});
  $('spExportStockBtn').addEventListener('click',function(){var rows=buildStockRows();var csv=[['规格名称','产品名称','总采购(次)','总采购数量','销量','手动加减','合计销量','现库存','平均单价','库存成本']];rows.forEach(function(r){csv.push([r.skuName,r.productName,r.totalPurCount,r.totalPurQty,r.soldQty||0,r.manualAdjust,r.totalSold,r.currentStock,r.avgUnitPrice.toFixed(2),r.stockCost.toFixed(2)]);});exportCSV('shopee库存.csv',csv);});
  $('spStockTable').addEventListener('change',function(e){
    if(e.target.classList.contains('stock-manual-input')){
      var sku=e.target.dataset.sku;
      var val=parseInt(e.target.value)||0;
      spStockManual[sku]=val;
      saveData(SK.spStockManual,spStockManual);
      renderStockTable();
      showToast('已保存手动调整');
    }
  });
}};

// ---------- Shopee: Ads (广告支出表 - 分站点) ----------
var adsSiteFilter='ph';
function getSiteSymbol(sid){var s=getSite(sid);return s?s.symbol:'';}
function renderAdsSiteTabs(){
  var el=$('spAdsSiteTabs');if(!el)return;
  var sites=calcSitesEnabled();
  el.innerHTML=sites.map(function(s){return '<div class="sp-range-tab'+(s.id===adsSiteFilter?' active':'')+'" data-site="'+s.id+'">'+s.name+'</div>';}).join('');
  el.querySelectorAll('.sp-range-tab').forEach(function(t){t.addEventListener('click',function(){adsSiteFilter=t.dataset.site;renderAdsSiteTabs();renderAdsTable();});});
}
function renderAdsTable(){
  var el=$('spAdsTable');if(!el)return;
  var list=spAds.filter(function(a){return a.site===adsSiteFilter;});
  if(list.length===0){el.innerHTML='<tbody><tr><td style="text-align:center;padding:40px;color:var(--text-3)">还没有广告数据，点击「＋ 添加广告」</td></tr></tbody>';return;}
  var head='<thead><tr><th>日期</th><th>广告费(¥)</th><th>点击</th><th>曝光</th><th>订单</th><th>GMV(本币)</th><th>CPC</th><th>CTR</th><th>转化率</th><th>ROAS</th><th>备注</th><th></th></tr></thead>';
  var body='<tbody>'+list.map(function(a){
    var cpc=a.clicks>0?(a.adSpend||0)/a.clicks:0;
    var ctr=a.impressions>0?(a.clicks/a.impressions*100).toFixed(2)+'%':'—';
    var cvr=a.clicks>0?(a.orders/a.clicks*100).toFixed(2)+'%':'—';
    var roas=a.adSpend>0?((a.gmv||0)/(a.adSpend||0)).toFixed(2):'—';
    return '<tr><td>'+fmtDate(a.date)+'</td><td class="num">¥'+fmtNum(a.adSpend||0)+'</td><td class="num">'+(a.clicks||0)+'</td><td class="num">'+(a.impressions||0)+'</td><td class="num">'+(a.orders||0)+'</td><td class="num">'+getSiteSymbol(a.site)+fmtNum(a.gmv||0)+'</td><td class="num">¥'+fmtNum(cpc)+'</td><td class="num">'+ctr+'</td><td class="num">'+cvr+'</td><td class="num">'+roas+'</td><td>'+escapeHtml(a.remark||'')+'</td><td><button class="act-btn" data-ads-edit="'+a.id+'">✏️</button><button class="act-btn danger" data-ads-del="'+a.id+'">🗑️</button></td></tr>';
  }).join('')+'</tbody>';
  var totalSpend=list.reduce(function(s,a){return s+(a.adSpend||0);},0);
  var totalClicks=list.reduce(function(s,a){return s+(a.clicks||0);},0);
  var totalOrders=list.reduce(function(s,a){return s+(a.orders||0);},0);
  var totalGMV=list.reduce(function(s,a){return s+(a.gmv||0);},0);
  body+='<tfoot><tr style="font-weight:bold;background:var(--bg-2)"><td>合计</td><td class="num">¥'+fmtNum(totalSpend)+'</td><td class="num">'+totalClicks+'</td><td></td><td class="num">'+totalOrders+'</td><td class="num">'+getSiteSymbol(adsSiteFilter)+fmtNum(totalGMV)+'</td><td colspan="5"></td></tr></tfoot>';
  el.innerHTML=head+body;
}
function showAdsForm(aid){
  editingDocId=aid||null;
  var a=aid?spAds.find(function(x){return x.id===aid;}):{date:todayStr(),site:adsSiteFilter,adSpend:'',clicks:'',impressions:'',orders:'',gmv:'',remark:''};
  $('spAdsModalTitle').textContent=aid?'编辑广告':'添加广告';
  var sopts=calcSitesEnabled().map(function(s){return '<option value="'+s.id+'"'+(a.site===s.id?' selected':'')+'>'+s.name+' ('+s.currency+')</option>';}).join('');
  $('spAdsFormBody').innerHTML=
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">日期</label><input class="input" id="adsDate" type="date" value="'+escapeAttr(a.date||todayStr())+'"></div><div class="form-group" style="flex:1"><label class="form-label">站点</label><select class="input" id="adsSite">'+sopts+'</select></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">广告费(¥)</label><input class="input" id="adsSpend" type="number" step="0.01" value="'+(a.adSpend||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">点击数</label><input class="input" id="adsClicks" type="number" value="'+(a.clicks||'')+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">曝光数</label><input class="input" id="adsImp" type="number" value="'+(a.impressions||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">订单数</label><input class="input" id="adsOrders" type="number" value="'+(a.orders||'')+'"></div></div>'+
    '<div class="form-row"><div class="form-group" style="flex:1"><label class="form-label">GMV(本币)</label><input class="input" id="adsGmv" type="number" step="0.01" value="'+(a.gmv||'')+'"></div><div class="form-group" style="flex:1"><label class="form-label">备注</label><input class="input" id="adsRemark" value="'+escapeAttr(a.remark||'')+'"></div></div>'+
    '<div style="margin-top:8px;font-size:12px;color:var(--text-3)">💡 CPC=广告费÷点击，CTR=点击÷曝光，转化率=订单÷点击，ROAS=GMV÷广告费，均自动计算。</div>';
  $('spAdsModal').classList.add('open');$('spAdsModalMask').classList.add('open');
}
function closeAdsForm(){$('spAdsModal').classList.remove('open');$('spAdsModalMask').classList.remove('open');editingDocId=null;}
function saveAds(){
  var id=editingDocId||genId();
  var a={id:id,date:$('adsDate').value,site:$('adsSite').value,adSpend:parseFloat($('adsSpend').value)||0,clicks:parseInt($('adsClicks').value)||0,impressions:parseInt($('adsImp').value)||0,orders:parseInt($('adsOrders').value)||0,gmv:parseFloat($('adsGmv').value)||0,remark:$('adsRemark').value.trim()};
  if(editingDocId){var idx=spAds.findIndex(function(x){return x.id===id;});if(idx>=0)spAds[idx]=a;else spAds.push(a);}else spAds.push(a);
  saveData(SK.spAds,spAds);
  adsSiteFilter=a.site;
  closeAdsForm();
  renderAdsSiteTabs();
  renderAdsTable();
  showToast('已保存');
}
MODULES['sp-ads']={title:'广告支出',render:function(){
  return '<div class="section"><div class="toolbar"><button class="btn btn-primary" id="spAddAdsBtn">＋ 添加广告</button><button class="btn" id="spExportAdsBtn">📤 导出</button></div><div class="sp-range-tabs" id="spAdsSiteTabs"></div><div class="table-wrap"><table class="data-table" id="spAdsTable"></table></div>'+
    '<div class="modal-mask" id="spAdsModalMask"></div><div class="modal" id="spAdsModal"><div class="modal-title"><span id="spAdsModalTitle">添加广告</span><button class="modal-close" id="spAdsModalClose">✕</button></div><div id="spAdsFormBody"></div><div class="modal-actions"><button class="btn btn-primary" id="spSaveAdsBtn">保存</button><button class="btn" id="spCancelAdsBtn">取消</button></div></div></div>';
},init:function(){
  var se=calcSitesEnabled();
  if(!se.length||se.every(function(s){return s.id!==adsSiteFilter;})){if(se.length)adsSiteFilter=se[0].id;}
  renderAdsSiteTabs();
  renderAdsTable();
  $('spAddAdsBtn').addEventListener('click',function(){showAdsForm(null);});
  $('spSaveAdsBtn').addEventListener('click',saveAds);
  $('spCancelAdsBtn').addEventListener('click',closeAdsForm);
  $('spAdsModalClose').addEventListener('click',closeAdsForm);
  $('spAdsModalMask').addEventListener('click',closeAdsForm);
  $('spExportAdsBtn').addEventListener('click',function(){var rows=[['日期','站点','广告费(¥)','点击数','曝光数','订单数','GMV(本币)','备注']];spAds.forEach(function(a){rows.push([a.date,a.site,a.adSpend,a.clicks,a.impressions,a.orders,a.gmv,a.remark]);});exportCSV('shopee广告.csv',rows);});
  $('spAdsTable').addEventListener('click',function(e){
    var eb=e.target.closest('[data-ads-edit]');var db=e.target.closest('[data-ads-del]');
    if(eb)showAdsForm(eb.dataset.adsEdit);
    if(db){if(confirm('删除该广告记录？')){spAds=spAds.filter(function(x){return x.id!==db.dataset.adsDel;});saveData(SK.spAds,spAds);renderAdsTable();showToast('已删除');}}
  });
}};
