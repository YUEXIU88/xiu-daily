# -*- coding: utf-8 -*-
# V79: 1) 记账本+还款本  2) 标题移到图片旁边  3) 折扣恢复到标题下方 + SKU 价格完整显示
import io, sys

path = 'index.html'
src = io.open(path, 'r', encoding='utf-8').read()
orig_len = len(src)
changes = []

def rep(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, '[%s] match count=%d (expect %d)' % (label, n, count)
    src = src.replace(old, new)
    changes.append(label)

# ============ A1. NAV_TREE 增加记账本/还款本（\uXXXX 转义区，用 raw string） ============
old = r"""    {id:'ps-notes',name:'\u7b14\u8bb0\u672c',icon:'\ud83d\udccb'},"""
new = r"""    {id:'ps-notes',name:'\u7b14\u8bb0\u672c',icon:'\ud83d\udccb'},
    {id:'ps-ledger',name:'\u8bb0\u8d26\u672c',icon:'\ud83d\udcb0'},
    {id:'ps-debt',name:'\u8fd8\u6b3e\u672c',icon:'\ud83d\udcb3'},"""
rep(old, new, 'NAV_TREE')

# ============ A2. SK 存储键 ============
rep("psNotes:'xiu_ps_notes_v1',psPeriods:'xiu_ps_periods_v1',",
    "psNotes:'xiu_ps_notes_v1',psPeriods:'xiu_ps_periods_v1',psLedger:'xiu_ps_ledger_v1',psDebts:'xiu_ps_debts_v1',",
    'SK keys')

# ============ A3. 状态变量 ============
rep("var psNotes=[],psPeriods=[];",
    "var psNotes=[],psPeriods=[],psLedger=[],psDebts=[];",
    'state vars')

# ============ A4. loadAllData ============
rep("psNotes=loadData(SK.psNotes,[]);psPeriods=loadData(SK.psPeriods,[]);",
    "psNotes=loadData(SK.psNotes,[]);psPeriods=loadData(SK.psPeriods,[]);psLedger=loadData(SK.psLedger,[]);psDebts=loadData(SK.psDebts,[]);",
    'loadAllData')

# ============ A5. saveAllData ============
rep("saveData(SK.psNotes,psNotes);saveData(SK.psPeriods,psPeriods);",
    "saveData(SK.psNotes,psNotes);saveData(SK.psPeriods,psPeriods);saveData(SK.psLedger,psLedger);saveData(SK.psDebts,psDebts);",
    'saveAllData')

# ============ A6. collectAllData 云同步上传 ============
rep("psNotes:psNotes,psPeriods:psPeriods,",
    "psNotes:psNotes,psPeriods:psPeriods,psLedger:psLedger,psDebts:psDebts,",
    'collectAllData')

# ============ A7. applySyncData（先替换更长的唯一匹配，避免 A8 撞车） ============
rep("if(data.psNotes)psNotes=data.psNotes;if(data.psPeriods)psPeriods=data.psPeriods;",
    "if(data.psNotes)psNotes=data.psNotes;if(data.psPeriods)psPeriods=data.psPeriods;if(data.psLedger)psLedger=data.psLedger;if(data.psDebts)psDebts=data.psDebts;",
    'applySyncData')

# ============ A8. pullSyncData 云同步下载（按 id 合并） ============
old = "if(data.psPeriods)psPeriods=data.psPeriods;if(data.studyLog)"
new = ("if(data.psPeriods)psPeriods=data.psPeriods;"
       "if(data.psLedger){var _lgm={};(data.psLedger||[]).forEach(function(x){if(x&&x.id)_lgm[x.id]=x;});(psLedger||[]).forEach(function(x){if(x&&x.id)_lgm[x.id]=x;});psLedger=[];for(var _lgk in _lgm)psLedger.push(_lgm[_lgk]);}"
       "if(data.psDebts){var _dbm={};(data.psDebts||[]).forEach(function(x){if(x&&x.id)_dbm[x.id]=x;});(psDebts||[]).forEach(function(x){if(x&&x.id)_dbm[x.id]=x;});psDebts=[];for(var _dbk in _dbm)psDebts.push(_dbm[_dbk]);}"
       "if(data.studyLog)")
rep(old, new, 'pullSyncData')

# ============ B1. renderProductGrid 表头（去掉标题列） ============
rep('<th class="col-img" style="width:90px">图片</th><th class="col-title">上架标题 / 产品名</th><th class="col-cat">类目</th>',
    '<th class="col-img">图片 / 标题 / 价格</th><th class="col-cat">类目</th>',
    'thead')

# ============ B2. 行结构：图片+标题同行，折扣在标题下 ============
old = r"""var img='<div class="sp-tb-idx">#'+(idx+1)+'</div><div class="sp-tb-img-wrap">'+imgCore+'</div>';"""
new = r"""var img='<div class="sp-tb-left"><div class="sp-tb-idx">#'+(idx+1)+'</div><div class="sp-tb-img-wrap">'+imgCore+'</div></div>';"""
rep(old, new, 'img left wrap')

old = r"""'<tr data-pid="'+p.id+'" class="sp-main-row'+(exp?' exp':'')+'"><td class="col-img">'+img+renderProductPricePreview(p)+'</td><td class=\"col-title\">'+titleWrap+(p.title&&p.title!==p.name?'<div class=\"sp-tb-sub\">'+escapeHtml(p.name)+'</div>':'')+'</td><td class="col-cat">'"""
new = r"""'<tr data-pid="'+p.id+'" class="sp-main-row'+(exp?' exp':'')+'"><td class="col-img"><div class="sp-tb-head">'+img+'<div class="sp-tb-right">'+titleWrap+prodDiscInputs(p)+(p.title&&p.title!==p.name?'<div class=\"sp-tb-sub\">'+escapeHtml(p.name)+'</div>':'')+'</div></div>'+renderProductPricePreview(p)+'</td><td class="col-cat">'"""
rep(old, new, 'row structure')

# ============ B3. 展开行 colspan 6 -> 5 ============
old = r"""'<tr class="sp-detail-row'+(exp?' open':'')+'" data-pid="'+p.id+'"><td colspan="6">"""
new = r"""'<tr class="sp-detail-row'+(exp?' open':'')+'" data-pid="'+p.id+'"><td colspan="5">"""
rep(old, new, 'detail colspan')

# ============ C1. renderProductPricePreview 移除 SKU 行内折扣 mini ============
old = r"""  // 产品级折扣 mini（仅在首个 SKU 名后显示一次）
  var discInline=sites.map(function(s){
    var dv=(p.disc&&p.disc[s.id]!=null&&p.disc[s.id]!=="")?p.disc[s.id]:prodDisc(p,s.id);
    return '<span class="sp-pp-disc-mini" onclick="event.stopPropagation()"><b>'+s.name.charAt(0)+'</b><input class="sp-disc-prod-in sp-disc-mini-in" data-prod-disc="'+s.id+'" type="number" step="0.1" min="0" value="'+dv+'" onclick="this.select()" placeholder="0">%</span>';
  }).join('');
  var discHtml='<span class="sp-pp-disc-inline" onclick="event.stopPropagation()">'+discInline+'</span>';
"""
new = ""
rep(old, new, 'remove disc mini')

old = r"""  var lines=skus.map(function(sk,si){
    var isFirst=si===0;
    var skuLabel"""
new = r"""  var lines=skus.map(function(sk,si){
    var skuLabel"""
rep(old, new, 'remove isFirst')

old = r"""return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+(isFirst?discHtml:"")+costHtml+siteCells+'</div>';"""
new = r"""return '<div class="sp-pp-sku-line" onclick="event.stopPropagation()"><span class="sp-pp-sku-name">'+escapeHtml(skuLabel)+'</span>'+costHtml+siteCells+'</div>';"""
rep(old, new, 'sku line no disc')

# ============ C2. renderSkuSiteCalc 计算气泡缩短文字（修"只显示一半"） ============
old = r"""html+='<span class="sp-pp-final">折后 '+s.symbol+fmtNum(c.finalLocal)+'</span>';"""
new = r"""html+='<span class="sp-pp-final">'+s.symbol+fmtNum(c.finalLocal)+'</span>';"""
rep(old, new, 'calc final short')

old = r"""html+='<span class="sp-pp-profit '+profCls+'">利润 '+profSign+'¥'+fmtNum(Math.abs(c.profit))+'</span>';"""
new = r"""html+='<span class="sp-pp-profit '+profCls+'">'+profSign+'¥'+fmtNum(Math.abs(c.profit))+'</span>';"""
rep(old, new, 'calc profit short')

# ============ D1. CSS: col-img 加宽（修价格被截断） ============
old = r""".sp-prod-tbl .col-img{vertical-align:top;min-width:300px;max-width:560px;padding-top:6px;padding-left:10px;padding-right:6px}"""
new = r""".sp-prod-tbl .col-img{vertical-align:top;min-width:640px;max-width:none;padding-top:6px;padding-left:10px;padding-right:6px}
/* V79: 图片+标题同行结构 */
.sp-tb-head{display:flex;gap:10px;align-items:flex-start;margin-bottom:4px}
.sp-tb-left{flex:0 0 auto;display:flex;flex-direction:column;align-items:flex-start}
.sp-tb-right{flex:1 1 0;min-width:0;padding-top:2px}
.sp-tb-right .sp-tb-title{white-space:normal;overflow-wrap:break-word}
.sp-tb-right .sp-tb-title-wrap{width:auto;flex-wrap:wrap}"""
rep(old, new, 'col-img CSS + head CSS')

# ============ D2. CSS: SKU 行滚动条可见（细） ============
old = r""".sp-pp-sku-line::-webkit-scrollbar{height:0;display:none}.sp-pp-sku-line{scrollbar-width:thin;scrollbar-color:transparent transparent}"""
new = r""".sp-pp-sku-line::-webkit-scrollbar{height:4px}.sp-pp-sku-line{scrollbar-width:thin;scrollbar-color:var(--border) transparent}"""
rep(old, new, 'sku-line scrollbar')

# ============ D3. CSS: 价格输入框略窄 ============
old = r""".sp-pp-price-in{width:54px;"""
new = r""".sp-pp-price-in{width:46px;"""
rep(old, new, 'price input width')

# ============ D4. 删除 ≤520px 隐藏图片列（现在图片列包含全部内容） ============
rep('@media(max-width:520px){.sp-prod-tbl .col-img{display:none}}',
    '/* V79: 图片列含标题+价格，不再隐藏 */',
    'remove hide col-img')

# ============ D5. 移动端布局适配 ============
old = r""".sp-prod-tbl .col-img{display:block!important;flex:none}"""
new = r""".sp-prod-tbl .col-img{display:block!important;flex:1 1 100%;min-width:0}"""
rep(old, new, 'mobile col-img')

old = r""".sp-prod-tbl .col-title{flex:1 1 150px;min-width:0}"""
new = r""""""
rep(old, new, 'mobile col-title removed')

# ============ E. 记账本 + 还款本 模块代码（插在 ps-period 之后） ============
anchor = r"""MODULES['ps-period']={title:'经期记录',render:function(){return '<div class="section"><div id="periodCal"></div></div>';},init:function(){renderPeriodCal();}};"""
assert src.count(anchor) == 1, 'ps-period anchor count=%d' % src.count(anchor)

module_code = u"""

// ---------- Personal: Ledger 记账本 (V79) ----------
function ledgerMonthKey(d){return String(d||'').slice(0,7);}
function renderLedgerView(){
  var el=$('psLedgerView');if(!el)return;
  var nowM=todayStr().slice(0,7);
  if(!window._lgMonth)window._lgMonth=nowM;
  var months={};psLedger.forEach(function(r){months[ledgerMonthKey(r.date)]=1;});
  var mOpts='<option value="">全部</option>'+Object.keys(months).sort().reverse().map(function(m){return '<option value="'+m+'"'+(window._lgMonth===m?' selected':'')+'>'+m+'</option>';}).join('');
  var all=psLedger.slice().sort(function(a,b){return a.date<b.date?1:-1;});
  var list=window._lgMonth?all.filter(function(r){return ledgerMonthKey(r.date)===window._lgMonth;}):all;
  var exp=0,inc=0;list.forEach(function(r){var v=parseFloat(r.amount)||0;if(r.type==='income')inc+=v;else exp+=v;});
  var fm=window._lgEdit?psLedger.find(function(x){return x.id===window._lgEdit;}):null;
  var formHtml='<div class="lg-form"><div class="lg-form-title">'+(fm?'✏️ 编辑记录':'＋ 记一笔')+'</div>'+
    '<div class="lg-form-grid">'+
    '<input class="input" id="lgDate" type="date" value="'+(fm?fm.date:todayStr())+'" title="日期">'+
    '<select class="input" id="lgType"><option value="expense"'+((fm?fm.type:'expense')==='expense'?' selected':'')+'>💸 支出</option><option value="income"'+((fm?fm.type:'')==='income'?' selected':'')+'>💰 收入</option></select>'+
    '<input class="input" id="lgAmount" type="number" inputmode="decimal" step="0.01" min="0" placeholder="金额 ¥" value="'+(fm?String(fm.amount||''):'')+'">'+
    '<input class="input" id="lgNote" placeholder="备注（如：运费、货款、房租）" value="'+escapeAttr(fm?fm.note||'':'')+'">'+
    '</div><div class="lg-form-actions"><button class="btn btn-primary" id="lgSaveBtn">'+(fm?'更新':'保存')+'</button>'+(fm?'<button class="btn" id="lgCancelEditBtn">取消</button>':'')+'</div></div>';
  var rows=list.map(function(r){
    var t=r.type==='income';
    return '<div class="lg-row" data-lgedit="'+r.id+'" title="点击编辑"><span class="lg-date">'+fmtDate(r.date)+'</span><span class="lg-badge '+(t?'lg-badge-inc':'lg-badge-exp')+'">'+(t?'💰 收入':'💸 支出')+'</span><span class="lg-amount '+(t?'pos':'neg')+'">'+(t?'+':'−')+'¥'+fmtNum(r.amount)+'</span><span class="lg-note">'+escapeHtml(r.note||'')+'</span><button class="act-btn danger" data-lgdel="'+r.id+'" title="删除">🗑️</button></div>';
  }).join('');
  if(!list.length)rows='<div class="empty-state"><div class="empty-state-icon">💰</div><p>还没有记录</p><p style="font-size:13px;color:var(--text-3)">用上方表单记一笔收支</p></div>';
  el.innerHTML='<div class="lg-stats">'+
    '<div class="lg-stat"><span>支出</span><b class="neg">¥'+fmtNum(exp)+'</b></div>'+
    '<div class="lg-stat"><span>收入</span><b class="pos">¥'+fmtNum(inc)+'</b></div>'+
    '<div class="lg-stat"><span>结余</span><b class="'+(inc-exp>=0?'pos':'neg')+'">'+(inc-exp>=0?'+':'−')+'¥'+fmtNum(Math.abs(inc-exp))+'</b></div>'+
    '</div>'+formHtml+
    '<div class="toolbar" style="margin:12px 0 8px"><span class="section-title" style="margin:0">📝 记录（'+list.length+'）</span><select class="input" id="lgMonthSel" style="margin-left:auto;max-width:150px">'+mOpts+'</select></div>'+
    '<div id="lgList">'+rows+'</div>';
  $('lgMonthSel').addEventListener('change',function(){window._lgMonth=this.value;renderLedgerView();});
  $('lgSaveBtn').addEventListener('click',function(){
    var d=$('lgDate').value||todayStr();var t=$('lgType').value;var a=parseFloat($('lgAmount').value);var n=$('lgNote').value.trim();
    if(!a||a<=0){showToast('请输入金额');return;}
    if(window._lgEdit){var ix=psLedger.findIndex(function(x){return x.id===window._lgEdit;});if(ix>-1)psLedger[ix]={id:window._lgEdit,date:d,type:t,amount:a,note:n};}
    else psLedger.push({id:genId(),date:d,type:t,amount:a,note:n});
    window._lgEdit=null;saveData(SK.psLedger,psLedger);renderLedgerView();showToast('已保存');
  });
  var cb=$('lgCancelEditBtn');if(cb)cb.addEventListener('click',function(){window._lgEdit=null;renderLedgerView();});
  el.querySelectorAll('[data-lgdel]').forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();if(confirm('删除该记录？')){var id=b.dataset.lgdel;psLedger=psLedger.filter(function(x){return x.id!==id;});if(window._lgEdit===id)window._lgEdit=null;saveData(SK.psLedger,psLedger);renderLedgerView();showToast('已删除');}});});
  el.querySelectorAll('[data-lgedit]').forEach(function(rw){rw.addEventListener('click',function(){window._lgEdit=rw.dataset.lgedit;renderLedgerView();});});
}
MODULES['ps-ledger']={title:'记账本',render:function(){
  return '<div class="section"><div id="psLedgerView"></div></div>';
},init:function(){renderLedgerView();}};

// ---------- Personal: Debt 还款本 (V79) ----------
function renderDebtView(){
  var el=$('psDebtView');if(!el)return;
  var today=todayStr();var nowM=today.slice(0,7);
  var all=psDebts.slice().sort(function(a,b){return a.date<b.date?1:-1;});
  var monthAll=0,monthPaid=0,monthLeft=0,totalLeft=0,nextDate=null;
  all.forEach(function(r){var v=parseFloat(r.amount)||0;var mk=String(r.date).slice(0,7);if(mk===nowM){monthAll+=v;if(r.paid)monthPaid+=v;else monthLeft+=v;}if(!r.paid){totalLeft+=v;if(!nextDate||r.date<nextDate)nextDate=r.date;}});
  var fm=window._dbEdit?psDebts.find(function(x){return x.id===window._dbEdit;}):null;
  var formHtml='<div class="lg-form"><div class="lg-form-title">'+(fm?'✏️ 编辑还款项':'＋ 添加还款项')+'</div>'+
    '<div class="lg-form-grid">'+
    '<input class="input" id="dbDate" type="date" value="'+(fm?fm.date:today)+'" title="还款日期">'+
    '<input class="input" id="dbAmount" type="number" inputmode="decimal" step="0.01" min="0" placeholder="金额 ¥" value="'+(fm?String(fm.amount||''):'')+'">'+
    '<input class="input" id="dbNote" placeholder="备注（如：花呗、房贷、货款）" value="'+escapeAttr(fm?fm.note||'':'')+'">'+
    '</div><div class="lg-form-actions"><button class="btn btn-primary" id="dbSaveBtn">'+(fm?'更新':'保存')+'</button>'+(fm?'<button class="btn" id="dbCancelEditBtn">取消</button>':'')+'</div></div>';
  var groups={};all.forEach(function(r){var mk=String(r.date).slice(0,7);if(!groups[mk])groups[mk]=[];groups[mk].push(r);});
  var mks=Object.keys(groups).sort().reverse();
  var monthHtml=mks.map(function(mk){
    var g=groups[mk];var ga=0,gp=0,gl=0;
    g.forEach(function(r){var v=parseFloat(r.amount)||0;ga+=v;if(r.paid)gp+=v;else gl+=v;});
    var rows=g.map(function(r){
      var v=parseFloat(r.amount)||0;
      var statusHtml=r.paid?'<span class="db-badge db-badge-paid">✅ 已还</span>':'<span class="db-badge db-badge-unpaid">⏳ 未还</span>';
      var btn=r.paid?'<button class="act-btn" data-dbtoggle="'+r.id+'" title="撤销已还">↩️</button>':'<button class="btn btn-primary" style="padding:2px 10px;font-size:12px" data-dbtoggle="'+r.id+'">✅ 已还</button>';
      return '<div class="db-row'+(r.paid?' db-row-paid':'')+'"><span class="lg-date">'+fmtDate(r.date)+'</span><span class="lg-note">'+escapeHtml(r.note||'还款')+'</span><span class="lg-amount neg">¥'+fmtNum(v)+'</span>'+statusHtml+btn+'<button class="act-btn danger" data-dbdel="'+r.id+'" title="删除">🗑️</button></div>';
    }).join('');
    return '<div class="db-month'+(mk===nowM?' db-month-now':'')+'"><div class="db-month-head"><b>'+mk.replace('-','年')+'月</b>'+(mk===nowM?'<span class="db-now-tag">本月</span>':'')+'<span class="db-month-sum">应还 ¥'+fmtNum(ga)+' · 已还 ¥'+fmtNum(gp)+' · <span class="'+(gl>0?'neg':'pos')+'">剩余 ¥'+fmtNum(gl)+'</span></span></div>'+rows+'</div>';
  }).join('');
  if(!mks.length)monthHtml='<div class="empty-state"><div class="empty-state-icon">💳</div><p>还没有还款记录</p><p style="font-size:13px;color:var(--text-3)">添加每月需还的金额，还了就点「✅ 已还」</p></div>';
  el.innerHTML='<div class="lg-stats">'+
    '<div class="lg-stat"><span>本月应还</span><b>¥'+fmtNum(monthAll)+'</b></div>'+
    '<div class="lg-stat"><span>本月已还</span><b class="pos">¥'+fmtNum(monthPaid)+'</b></div>'+
    '<div class="lg-stat"><span>本月剩余</span><b class="'+(monthLeft>0?'neg':'pos')+'">¥'+fmtNum(monthLeft)+'</b></div>'+
    '<div class="lg-stat"><span>总剩余欠款</span><b class="neg">¥'+fmtNum(totalLeft)+'</b></div>'+
    '</div>'+(nextDate?'<div class="db-next-tip">⏰ 最近待还：'+fmtDate(nextDate)+'，别忘了哦</div>':'')+formHtml+
    '<div class="section-title" style="margin:12px 0 6px">📅 每月还款计划</div>'+monthHtml;
  $('dbSaveBtn').addEventListener('click',function(){
    var d=$('dbDate').value||todayStr();var a=parseFloat($('dbAmount').value);var n=$('dbNote').value.trim();
    if(!a||a<=0){showToast('请输入金额');return;}
    if(window._dbEdit){var ix=psDebts.findIndex(function(x){return x.id===window._dbEdit;});if(ix>-1)psDebts[ix]={id:window._dbEdit,date:d,amount:a,note:n,paid:psDebts[ix].paid,paidAt:psDebts[ix].paidAt};}
    else psDebts.push({id:genId(),date:d,amount:a,note:n,paid:false,paidAt:null});
    window._dbEdit=null;saveData(SK.psDebts,psDebts);renderDebtView();showToast('已保存');
  });
  var cb2=$('dbCancelEditBtn');if(cb2)cb2.addEventListener('click',function(){window._dbEdit=null;renderDebtView();});
  el.querySelectorAll('[data-dbtoggle]').forEach(function(b){b.addEventListener('click',function(){
    var id=b.dataset.dbtoggle;var r=psDebts.find(function(x){return x.id===id;});if(!r)return;
    r.paid=!r.paid;r.paidAt=r.paid?Date.now():null;
    saveData(SK.psDebts,psDebts);renderDebtView();showToast(r.paid?'✅ 已标记还款':'已撤销');
  });});
  el.querySelectorAll('[data-dbdel]').forEach(function(b){b.addEventListener('click',function(){
    if(confirm('删除该还款项？')){psDebts=psDebts.filter(function(x){return x.id!==b.dataset.dbdel;});saveData(SK.psDebts,psDebts);renderDebtView();showToast('已删除');}
  });});
}
MODULES['ps-debt']={title:'还款本',render:function(){
  return '<div class="section"><div id="psDebtView"></div></div>';
},init:function(){renderDebtView();}};
"""
src = src.replace(anchor, anchor + module_code)
changes.append('insert ledger+debt modules')

# ============ F. 记账本/还款本 CSS（追加到 sp-pp-date-cell 之后） ============
css_anchor = r""".sp-pp-date-cell{white-space:nowrap}"""
assert src.count(css_anchor) == 1
css_new = css_anchor + r"""
/* V79: 记账本/还款本 */
.lg-stats{display:flex;gap:8px;flex-wrap:wrap}
.lg-stat{flex:1;min-width:110px;background:var(--bg);border:1px solid var(--border-l);border-radius:10px;padding:8px 12px;display:flex;flex-direction:column;gap:2px}
.lg-stat span{font-size:11px;color:var(--text-3)}
.lg-stat b{font-size:16px;line-height:1.3}
.lg-stat b.pos{color:var(--success)}.lg-stat b.neg{color:var(--danger)}
.lg-form{background:var(--bg);border:1px solid var(--border-l);border-radius:12px;padding:10px;margin-top:10px}
.lg-form-title{font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text)}
.lg-form-grid{display:flex;gap:8px;flex-wrap:wrap}
.lg-form-grid .input{flex:1;min-width:130px}
.lg-form-actions{display:flex;gap:8px;margin-top:8px}
.lg-row,.db-row{display:flex;align-items:center;gap:8px;padding:7px 10px;background:var(--card);border:1px solid var(--border-l);border-radius:10px;margin-bottom:6px;flex-wrap:wrap;cursor:pointer}
.lg-row:hover{border-color:var(--primary)}
.db-row{cursor:default}
.lg-date{font-size:12px;color:var(--text-3);white-space:nowrap;min-width:74px}
.lg-amount{font-weight:700;font-size:13.5px;white-space:nowrap}
.lg-amount.pos{color:var(--success)}.lg-amount.neg{color:var(--danger)}
.lg-note{font-size:12.5px;color:var(--text-2);flex:1;min-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lg-badge{font-size:11px;padding:1px 8px;border-radius:10px;white-space:nowrap}
.lg-badge-inc{background:rgba(46,160,67,.12);color:#2ea043}
.lg-badge-exp{background:rgba(217,83,79,.12);color:#d9534f}
.db-month{margin-bottom:12px}
.db-month-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:6px 10px;background:var(--bg-2);border-radius:10px;margin-bottom:6px;font-size:12.5px}
.db-month-head b{font-size:13px}
.db-month-now .db-month-head{background:var(--primary-l)}
.db-now-tag{font-size:10.5px;font-weight:700;color:#fff;background:var(--primary);border-radius:8px;padding:1px 8px}
.db-month-sum{margin-left:auto;color:var(--text-3);font-size:11.5px;white-space:nowrap}
.db-month-sum .pos{color:var(--success)}.db-month-sum .neg{color:var(--danger)}
.db-row-paid{opacity:.62}
.db-row-paid .lg-amount{text-decoration:line-through}
.db-badge{font-size:11px;font-weight:600;padding:1px 8px;border-radius:10px;white-space:nowrap}
.db-badge-paid{background:rgba(46,160,67,.12);color:#2ea043}
.db-badge-unpaid{background:rgba(219,171,9,.15);color:#b8860b}
.db-next-tip{margin-top:8px;font-size:12.5px;color:var(--primary);background:var(--primary-l);border-radius:8px;padding:6px 10px}"""
src = src.replace(css_anchor, css_new)
changes.append('ledger/debt CSS')

# ============ G. 版本号 78 -> 79 ============
rep('var APP_VERSION=78;', 'var APP_VERSION=79;', 'APP_VERSION')

io.open(path, 'w', encoding='utf-8').write(src)
print('OK, %d changes:' % len(changes))
for c in changes:
    print(' - ' + c)
print('size: %d -> %d bytes (+%d)' % (orig_len, len(src), len(src) - orig_len))
