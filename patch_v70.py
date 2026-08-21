# -*- coding: utf-8 -*-
"""V70: 笔记本富文本编辑器 - contenteditable + 工具栏"""
import sys

p = r'C:\Users\92809\WorkBuddy\2026-08-19-23-27-21\english-sentences\index.html'
src = open(p, encoding='utf-8').read()
orig = src

# ---------- 1) 富文本 CSS ----------
css_anchor = ".note-editor{background:var(--card);border:1px solid var(--border);border-radius:var(--r-sm);padding:16px;margin-bottom:12px}"
RICH_CSS = """
/* ===== Rich Text Editor (notebook) ===== */
.ne-toolbar{display:flex;flex-wrap:wrap;gap:3px;padding:7px 9px;background:var(--bg-2);border:1px solid var(--border-l);border-bottom:none;border-radius:var(--r-sm) var(--r-sm) 0 0;align-items:center}
.ne-toolbar .ne-tbtn{min-width:30px;height:28px;padding:0 7px;border:1px solid var(--border-l);background:var(--card);border-radius:5px;font-size:12.5px;font-weight:600;cursor:pointer;color:var(--text-2);display:inline-flex;align-items:center;justify-content:center;transition:var(--tr);user-select:none}
.ne-toolbar .ne-tbtn:hover{background:var(--primary-l);border-color:var(--primary);color:var(--primary)}
.ne-toolbar .ne-tbtn.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.ne-toolbar .ne-sep{width:1px;height:18px;background:var(--border-l);margin:0 2px;flex-shrink:0}
.ne-color-wrap{position:relative;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center}
.ne-color-wrap input[type=color]{position:absolute;inset:0;width:100%;height:100%;border:none;background:none;cursor:pointer;opacity:0;padding:0}
.ne-color-dot{width:18px;height:18px;border-radius:4px;border:1px solid var(--border);background:linear-gradient(135deg,#ff5b5b 0%,#ffb300 25%,#2ea043 50%,#2f80ed 75%,#b15cff 100%);pointer-events:none}
.ne-rt{min-height:220px;max-height:520px;overflow-y:auto;padding:14px 16px;border:1px solid var(--border-l);border-top:none;border-radius:0 0 var(--r-sm) var(--r-sm);background:var(--card);font-size:15px;line-height:1.75;outline:none;word-break:break-word}
.ne-rt:focus{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary-l)}
.ne-rt:empty:before{content:attr(data-placeholder);color:var(--text-3);font-style:italic}
.ne-rt h2{font-size:20px;font-weight:700;margin:14px 0 6px;line-height:1.3}
.ne-rt h3{font-size:17px;font-weight:700;margin:10px 0 4px;line-height:1.3}
.ne-rt p{margin:4px 0}
.ne-rt ul,.ne-rt ol{margin:6px 0;padding-left:26px}
.ne-rt ul{list-style:disc}
.ne-rt ol{list-style:decimal}
.ne-rt li{margin:2px 0}
.ne-rt blockquote{border-left:3px solid var(--primary);margin:8px 0;padding:6px 14px;color:var(--text-2);background:var(--bg-2);border-radius:0 6px 6px 0;font-style:italic}
.ne-rt a{color:var(--primary);text-decoration:underline}
.ne-rt font[size="1"]{font-size:13px}
.ne-rt font[size="2"]{font-size:15px}
.ne-rt font[size="3"]{font-size:18px}
.ne-rt font[size="4"]{font-size:22px}
.ne-rt font[size="5"]{font-size:28px}
.ne-rt font[size="6"]{font-size:36px}
.ne-rt font[size="7"]{font-size:48px}"""
assert css_anchor in src, "CSS anchor not found"
src = src.replace(css_anchor, css_anchor + "\n" + RICH_CSS, 1)

# ---------- 2) 辅助函数 + preview ----------
helper_anchor = "// ---------- Personal: Notes ----------\nfunction renderNotesList(){"
HELPERS = """// ---------- Personal: Notes ----------
function noteContentToHtml(c){
  if(!c)return '';
  if(/<[a-z][\\s\\S]*>/i.test(c))return c;
  return escapeHtml(c).replace(/\\n/g,'<br>');
}
function noteContentPreview(c){
  if(!c)return '';
  if(/<[a-z][\\s\\S]*>/i.test(c)){var d=document.createElement('div');d.innerHTML=c;return escapeHtml((d.textContent||'').slice(0,80));}
  return escapeHtml(c.slice(0,80));
}"""
assert helper_anchor in src, "helper anchor not found"
src = src.replace(helper_anchor, HELPERS + "\nfunction renderNotesList(){", 1)

# ---------- 3) preview in list (regex, robust to quote escaping) ----------
import re
pat = re.compile(r"escapeHtml\(\(n\.content\|\|''\)\.slice\(0,80\)\)")
assert pat.search(src), "preview pattern not found"
src = pat.sub("noteContentPreview(n.content)", src, count=1)

# ---------- 4) openNoteEditor 整体替换 ----------
i0 = src.index("function openNoteEditor(nid){")
i1 = src.index("function closeNoteEditor(){")
NEW_OPEN = '''function openNoteEditor(nid){
  editingNoteId=nid||null;
  var n=nid?psNotes.find(function(x){return x.id===nid;}):{title:'',content:''};
  if(!n)n={title:'',content:''};
  $('psNoteEditor').innerHTML=
    '<div class="form-group"><input class="input" id="neTitle" value="'+escapeAttr(n.title||'')+'" placeholder="标题" style="font-size:16px;font-weight:600"></div>'+
    '<div class="ne-toolbar" id="neToolbar">'+
      '<button class="ne-tbtn" data-cmd="bold" title="加粗" style="font-weight:800">B</button>'+
      '<button class="ne-tbtn" data-cmd="italic" title="斜体" style="font-style:italic">I</button>'+
      '<button class="ne-tbtn" data-cmd="underline" title="下划线" style="text-decoration:underline">U</button>'+
      '<button class="ne-tbtn" data-cmd="strikeThrough" title="删除线" style="text-decoration:line-through">S</button>'+
      '<span class="ne-sep"></span>'+
      '<button class="ne-tbtn" data-block="H2" title="标题2">H2</button>'+
      '<button class="ne-tbtn" data-block="H3" title="标题3">H3</button>'+
      '<button class="ne-tbtn" data-block="P" title="正文段落">正文</button>'+
      '<span class="ne-sep"></span>'+
      '<button class="ne-tbtn" data-cmd="insertUnorderedList" title="无序列表">•</button>'+
      '<button class="ne-tbtn" data-cmd="insertOrderedList" title="有序列表">1.</button>'+
      '<button class="ne-tbtn" data-block="BLOCKQUOTE" title="引用">❝</button>'+
      '<span class="ne-sep"></span>'+
      '<button class="ne-tbtn" data-cmd="justifyLeft" title="左对齐">⬅</button>'+
      '<button class="ne-tbtn" data-cmd="justifyCenter" title="居中">↔</button>'+
      '<button class="ne-tbtn" data-cmd="justifyRight" title="右对齐">➡</button>'+
      '<span class="ne-sep"></span>'+
      '<button class="ne-tbtn" data-fsize="1" title="小字">小</button>'+
      '<button class="ne-tbtn" data-fsize="3" title="中字">中</button>'+
      '<button class="ne-tbtn" data-fsize="5" title="大字">大</button>'+
      '<span class="ne-sep"></span>'+
      '<span class="ne-color-wrap"><span class="ne-color-dot"></span><input type="color" id="neColorPicker" title="文字颜色" value="#ff6698"></span>'+
      '<span class="ne-sep"></span>'+
      '<button class="ne-tbtn" data-cmd="undo" title="撤销">↶</button>'+
      '<button class="ne-tbtn" data-cmd="redo" title="重做">↷</button>'+
      '<button class="ne-tbtn" data-cmd="removeFormat" title="清除格式">✕</button>'+
    '</div>'+
    '<div class="ne-rt" id="neContent" contenteditable="true" data-placeholder="写点什么..." spellcheck="true">'+noteContentToHtml(n.content||'')+'</div>'+
    '<div class="toolbar" style="margin-top:8px"><button class="btn btn-primary" id="neSaveBtn">💾 保存</button><button class="btn" id="neDelBtn">🗑️ 删除</button><button class="btn" id="neBackBtn">← 返回</button></div>';
  $('psNoteEditor').style.display='block';$('psNotesList').style.display='none';
  var rt=$('neContent');
  var neSavedRange=null;
  function neSaveSel(){var s=window.getSelection();if(s&&s.rangeCount&&rt.contains(s.anchorNode))neSavedRange=s.getRangeAt(0).cloneRange();}
  function neRestoreSel(){rt.focus();if(neSavedRange){var s=window.getSelection();s.removeAllRanges();s.addRange(neSavedRange);}}
  rt.addEventListener('keyup',neSaveSel);
  rt.addEventListener('mouseup',neSaveSel);
  function updateNeToolbar(){
    ['bold','italic','underline','strikeThrough'].forEach(function(cmd){
      var btn=$('neToolbar').querySelector('[data-cmd="'+cmd+'"]');
      if(btn){try{btn.classList.toggle('active',document.queryCommandState(cmd));}catch(e){}}
    });
  }
  rt.addEventListener('keyup',updateNeToolbar);
  rt.addEventListener('mouseup',updateNeToolbar);
  $('neToolbar').addEventListener('mousedown',function(e){if(e.target.closest('.ne-tbtn'))e.preventDefault();});
  $('neToolbar').addEventListener('click',function(e){
    var b=e.target.closest('.ne-tbtn');if(!b)return;
    rt.focus();neRestoreSel();
    if(b.dataset.cmd){document.execCommand(b.dataset.cmd,false,null);}
    else if(b.dataset.block){document.execCommand('formatBlock',false,b.dataset.block);}
    else if(b.dataset.fsize){document.execCommand('fontSize',false,b.dataset.fsize);}
    neSaveSel();updateNeToolbar();rt.focus();
  });
  var cp=$('neColorPicker');
  cp.addEventListener('mousedown',neSaveSel);
  cp.addEventListener('input',function(){rt.focus();neRestoreSel();document.execCommand('foreColor',false,this.value);neSaveSel();updateNeToolbar();});
  $('neSaveBtn').addEventListener('click',function(){
    var t=$('neTitle').value.trim();
    var cHtml=$('neContent').innerHTML;
    if(!rt.textContent.trim()&&!/<img|<table/i.test(cHtml))cHtml='';
    if(!t&&!cHtml){showToast('请输入内容');return;}
    if(editingNoteId){var idx=psNotes.findIndex(function(x){return x.id===editingNoteId;});if(idx>-1){psNotes[idx]={id:editingNoteId,title:t,content:cHtml,updatedAt:Date.now()};}}
    else{psNotes.push({id:genId(),title:t,content:cHtml,updatedAt:Date.now()});}
    saveData(SK.psNotes,psNotes);closeNoteEditor();renderNotesList();showToast('已保存');
  });
  $('neDelBtn').addEventListener('click',function(){if(!editingNoteId){closeNoteEditor();return;}if(confirm('删除该笔记？')){psNotes=psNotes.filter(function(x){return x.id!==editingNoteId;});saveData(SK.psNotes,psNotes);closeNoteEditor();renderNotesList();showToast('已删除');}});
  $('neBackBtn').addEventListener('click',closeNoteEditor);
}
'''
src = src[:i0] + NEW_OPEN + src[i1:]

assert src != orig, "no change applied"
open(p,'w',encoding='utf-8').write(src)
print("V70 patch applied OK, delta:", len(src)-len(orig), "bytes")
