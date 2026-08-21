# -*- coding: utf-8 -*-
"""
V71: 修复笔记保存丢失 + 加微信笔记式装饰功能
1. pullSyncData psNotes 从直接覆盖改为按 id 合并
2. pagehide 增加 psNotes 保存
3. doSync 15KB → 60KB
4. 工具栏新增：分割线 hr / emoji 图标面板 / 待办清单 checkbox
5. APP_VERSION → 71
"""
import re

src = open('index.html', 'r', encoding='utf-8').read()
orig = src

# ============ 1. pullSyncData psNotes 合并 ============
old_psnotes = "if(data.psNotes)psNotes=data.psNotes;"
new_psnotes = (
    "if(data.psNotes){var _nm={};"
    "(data.psNotes||[]).forEach(function(x){if(x&&x.id)_nm[x.id]=x;});"
    "(psNotes||[]).forEach(function(x){if(x&&x.id)_nm[x.id]=x;});"
    "psNotes=[];for(var _nk in _nm)psNotes.push(_nm[_nk]);}"
)
assert old_psnotes in src, "pullSyncData psNotes not found"
src = src.replace(old_psnotes, new_psnotes, 1)
print("1. pullSyncData psNotes merge: OK")

# ============ 2. pagehide 增加 psNotes 保存 ============
old_pagehide = (
    "var _lastAutoSync=0;window.addEventListener('pagehide',function(){"
    "if(window._spSaveTimer){clearTimeout(window._spSaveTimer);saveData(SK.spProducts,spProducts);}"
    "if(window._spDiscTimer){clearTimeout(window._spDiscTimer);saveData(SK.spProducts,spProducts);}"
    "});"
)
new_pagehide = (
    "var _lastAutoSync=0;window.addEventListener('pagehide',function(){"
    "if(window._spSaveTimer){clearTimeout(window._spSaveTimer);saveData(SK.spProducts,spProducts);}"
    "if(window._spDiscTimer){clearTimeout(window._spDiscTimer);saveData(SK.spProducts,spProducts);}"
    "saveData(SK.psNotes,psNotes);"
    "});"
)
assert old_pagehide in src, "pagehide not found"
src = src.replace(old_pagehide, new_pagehide, 1)
print("2. pagehide psNotes save: OK")

# ============ 3. doSync 15KB → 60KB ============
old_limit = "if(body.length>15000){showToast('同步数据过大('+Math.round(body.length/1024)+'KB)，请先导出备份');saveSyncStatus({lastTry:ts,ok:false,msg:'数据过大'});syncing=false;return false;}"
new_limit = "if(body.length>60000){showToast('同步数据过大('+Math.round(body.length/1024)+'KB)，请先导出备份');saveSyncStatus({lastTry:ts,ok:false,msg:'数据过大'});syncing=false;return false;}"
assert old_limit in src, "doSync limit not found"
src = src.replace(old_limit, new_limit, 1)
print("3. doSync limit 15K→60K: OK")

# ============ 4. CSS: 新增分割线/emoji面板/待办样式 ============
old_css_end = '.ne-rt font[size="7"]{font-size:48px}'
new_css = old_css_end + """
.ne-rt hr{border:none;border-top:2px dashed var(--border);margin:14px 0}
.ne-rt .ne-todo{display:flex;align-items:flex-start;gap:6px;margin:3px 0;cursor:pointer}
.ne-rt .ne-todo input[type=checkbox]{margin-top:4px;flex-shrink:0;accent-color:var(--primary)}
.ne-rt .ne-todo.done span{text-decoration:line-through;color:var(--text-3)}
.ne-emoji-panel{display:none;position:absolute;z-index:100;background:var(--card);border:1px solid var(--border-l);border-radius:var(--r-sm);padding:8px;max-width:320px;max-height:200px;overflow-y:auto;box-shadow:0 4px 16px rgba(0,0,0,0.12);flex-wrap:wrap;gap:2px}
.ne-emoji-panel.open{display:flex}
.ne-emoji-panel .ne-emoji-item{font-size:20px;width:30px;height:30px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;border-radius:4px;transition:var(--tr)}
.ne-emoji-panel .ne-emoji-item:hover{background:var(--primary-l);transform:scale(1.2)}"""
assert old_css_end in src, "CSS end not found"
src = src.replace(old_css_end, new_css, 1)
print("4. CSS additions: OK")

# ============ 5. 工具栏新增按钮 ============
# 在"清除格式"按钮后面、</div> 前面加新按钮
old_toolbar_end = (
    "      '<button class=\"ne-tbtn\" data-cmd=\"removeFormat\" title=\"清除格式\">✕</button>'+\n"
    "    '</div>'+"
)
new_toolbar_end = (
    "      '<button class=\"ne-tbtn\" data-cmd=\"removeFormat\" title=\"清除格式\">✕</button>'+\n"
    "      '<span class=\"ne-sep\"></span>'+\n"
    "      '<button class=\"ne-tbtn\" data-cmd=\"insertHorizontalRule\" title=\"分割线\">―</button>'+\n"
    "      '<button class=\"ne-tbtn\" id=\"neEmojiBtn\" title=\"表情图标\">😊</button>'+\n"
    "      '<button class=\"ne-tbtn\" id=\"neTodoBtn\" title=\"待办清单\">☑</button>'+\n"
    "      '<div class=\"ne-emoji-panel\" id=\"neEmojiPanel\"></div>'+\n"
    "    '</div>'+"
)
assert old_toolbar_end in src, "toolbar end not found"
src = src.replace(old_toolbar_end, new_toolbar_end, 1)
print("5. Toolbar buttons: OK")

# ============ 6. JS: emoji 面板 + 待办功能 ============
# 在 color picker handler 后面、saveBtn handler 前面插入新逻辑
old_save_start = "  $('neSaveBtn').addEventListener('click',function(){"
new_js_block = """  // ===== V71: 分割线/emoji/待办 =====
  var NE_EMOJIS=['😀','😎','🤔','😍','😭','😂','😅','🥰','😴','🤯','🥳','😱','🤗','🙄','😏','😬','🤤','🥺','😇','🤩','🔥','✨','⭐','🌟','💫','💯','🎉','🎊','🎈','🎁','🏆','🥇','💪','👍','👎','👏','🙌','🤝','✌️','🤞','👀','💀','👻','🤖','💩','🌸','🌺','🌻','🌹','🌷','🍀','🌿','🌱','🌳','🌞','🌈','☁️','🌧️','⚡','❄️','☃️','🌊','🍎','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍒','🍑','🥭','🍍','🥥','🍅','🥑','🥦','🌽','🍞','🧀','🍗','🍔','🍟','🍕','🌭','🌮','🌯','🍜','🍣','🍱','🍰','🧁','☕','🍵','🧋','🍺','🍷','🥤','💧','📝','✏️','📌','📍','📎','🔗','💡','🧠','❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','💕','💖','💘','💝','⚛️','🔔','📢','💬','💭','☠️','♻️','✅','❌','❗','❓','⚠️','🚫','💰','💸','💳','📦','🚚','✈️','🚗','🏠','🏢','🏫','🏥','🏪','🌐','🕑','📅','📊','📈','📉','🔍','🛒','📦','✉️','📞','📱','💻','⌨️','🖥️','🖨️','📷','🎮','🎵','🎶','🎬','🎤','🎧','_radio','🧲','🔒','🔑','🛡️','⚙️','🔧','🔨','🛠️','⚙️','🧰','🧲','🔮','🪄','🧪','🧫','🧬','🔬','🔭','📡','💉','🩹','🩺','💊','🚪','🛏️','🛋️','🚿','🛁','🪒','🧴','🧷','🧹','🧺','🧻','🪣','🧼','🪟','🛒','🎁','🎈','🎀','🛍️','💳','💲','💴','💶','💷','🪙','💰','💸','🧾','📈','📊'];
  var emojiPanel=$('neEmojiPanel');
  if(emojiPanel){
    emojiPanel.innerHTML=NE_EMOJIS.map(function(e){return '<span class="ne-emoji-item" data-emoji="'+e+'">'+e+'</span>';}).join('');
  }
  var neEmojiBtn=$('neEmojiBtn');
  if(neEmojiBtn){
    neEmojiBtn.addEventListener('mousedown',function(e){e.preventDefault();});
    neEmojiBtn.addEventListener('click',function(e){
      e.stopPropagation();
      if(emojiPanel)emojiPanel.classList.toggle('open');
    });
  }
  if(emojiPanel){
    emojiPanel.addEventListener('mousedown',function(e){e.preventDefault();});
    emojiPanel.addEventListener('click',function(e){
      var item=e.target.closest('.ne-emoji-item');
      if(!item)return;
      rt.focus();neRestoreSel();
      var emoji=item.dataset.emoji;
      document.execCommand('insertText',false,emoji);
      emojiPanel.classList.remove('open');
      neSaveSel();rt.focus();
    });
  }
  document.addEventListener('click',function(e){
    if(emojiPanel&&emojiPanel.classList.contains('open')){
      if(!emojiPanel.contains(e.target)&&e.target!==neEmojiBtn&&!neEmojiBtn.contains(e.target)){
        emojiPanel.classList.remove('open');
      }
    }
  });
  var neTodoBtn=$('neTodoBtn');
  if(neTodoBtn){
    neTodoBtn.addEventListener('mousedown',function(e){e.preventDefault();});
    neTodoBtn.addEventListener('click',function(){
      rt.focus();neRestoreSel();
      var sel=window.getSelection();
      var txt=sel&&sel.toString()?sel.toString():'待办事项';
      var html='<label class="ne-todo"><input type="checkbox"><span>'+escapeHtml(txt)+'</span></label>&#8203;';
      document.execCommand('insertHTML',false,html);
      neSaveSel();rt.focus();
    });
  }
  // 待办 checkbox 点击切换
  rt.addEventListener('click',function(e){
    var todo=e.target.closest('.ne-todo');
    if(!todo)return;
    if(e.target.tagName==='INPUT'&&e.target.type==='checkbox'){
      if(e.target.checked)todo.classList.add('done');
      else todo.classList.remove('done');
    }
  });
  // 分割线按钮走 data-cmd，toolbar click handler 已经处理 execCommand
  $('neSaveBtn').addEventListener('click',function(){"""

assert old_save_start in src, "saveBtn handler not found"
src = src.replace(old_save_start, new_js_block, 1)
print("6. JS emoji/todo handlers: OK")

# ============ 7. toolbar click handler 支持 insertHTML/insertText ============
# 已有 handler 在 2950-2956 行，需要加对 insertHorizontalRule 的特殊处理
# 实际上 data-cmd="insertHorizontalRule" 已经会被 `document.execCommand(b.dataset.cmd,false,null)` 处理
# 但 insertHTML 不在 data-cmd 里，是手动绑定的，所以不需要改 toolbar handler
# 不需要额外修改

# ============ 8. APP_VERSION → 71 ============
src = src.replace("var APP_VERSION=70;", "var APP_VERSION=71;", 1)
print("8. APP_VERSION → 71: OK")

# ============ Write ============
open('index.html','w',encoding='utf-8').write(src)
print("\n=== V71 patch applied, +%d bytes ===" % (len(src)-len(orig)))
