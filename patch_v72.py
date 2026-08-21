# -*- coding: utf-8 -*-
"""
V72: 笔记本加图片插入 + 语音转文字 + 工具栏微信化
1. 工具栏最左侧加 🎤 语音转文字 + 🖼️ 图片插入
2. CSS: .ne-rt img 样式（最大宽度100%，圆角）
3. JS: 图片压缩插入 + 语音识别实时转文字
4. doSync 策略：psNotes > 60KB 时跳过云同步（保留本地+提示）
5. APP_VERSION → 72
"""
import re

src = open('index.html', 'r', encoding='utf-8').read()
orig = src

# ============ 1. CSS: 图片样式 + 录音高亮 ============
old_css = '.ne-rt font[size="7"]{font-size:48px}'
new_css = (
    '.ne-rt font[size="7"]{font-size:48px}\n'
    '.ne-rt img{max-width:100%;height:auto;border-radius:6px;margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,0.08)}\n'
    '.ne-toolbar .ne-tbtn.recording{background:#d9534f;color:#fff;border-color:#d9534f;animation:neRecPulse 1s infinite}\n'
    '@keyframes neRecPulse{0%,100%{opacity:1}50%{opacity:0.55}}\n'
    '.ne-toolbar .ne-tbtn.voice-unsupported{opacity:0.35;cursor:not-allowed}'
)
assert old_css in src, "CSS font-size7 not found"
src = src.replace(old_css, new_css, 1)
print("1. CSS img + recording: OK")

# ============ 2. 工具栏最左侧加 🎤 🖼️ + 隐藏 file input ============
old_first_btn = "    '<div class=\"ne-toolbar\" id=\"neToolbar\">'+\n      '<button class=\"ne-tbtn\" data-cmd=\"bold\" title=\"加粗\" style=\"font-weight:800\">B</button>'+"
new_first_btn = (
    "    '<div class=\"ne-toolbar\" id=\"neToolbar\">'+\n"
    "      '<button class=\"ne-tbtn\" id=\"neVoiceBtn\" title=\"语音转文字\">🎤</button>'+\n"
    "      '<button class=\"ne-tbtn\" id=\"neImgBtn\" title=\"插入图片\">🖼️</button>'+\n"
    "      '<input type=\"file\" id=\"neImgInput\" accept=\"image/*\" style=\"display:none\">'+"
    "      '<span class=\"ne-sep\"></span>'+\n"
    "      '<button class=\"ne-tbtn\" data-cmd=\"bold\" title=\"加粗\" style=\"font-weight:800\">B</button>'+"
)
assert old_first_btn in src, "first toolbar button not found"
src = src.replace(old_first_btn, new_first_btn, 1)
print("2. Toolbar voice+image buttons: OK")

# ============ 3. JS: 图片插入 handler ============
# 在 emojiPanel handler 之前插入图片和语音逻辑
old_emoji_start = "  // ===== V71: 分割线/emoji/待办 ====="
new_js_block = """  // ===== V72: 图片插入 =====
  var neImgBtn=$('neImgBtn'),neImgInput=$('neImgInput');
  function neCompressImg(dataUrl,maxW,cb){
    var img=new Image();
    img.onload=function(){
      try{
        var sc=Math.min(1,maxW/Math.max(img.width,img.height));
        var cv=document.createElement('canvas');
        cv.width=Math.max(1,Math.round(img.width*sc));
        cv.height=Math.max(1,Math.round(img.height*sc));
        cv.getContext('2d').drawImage(img,0,0,cv.width,cv.height);
        cb(cv.toDataURL('image/jpeg',0.7));
      }catch(e){cb(null);}
    };
    img.onerror=function(){cb(null);};
    img.src=dataUrl;
  }
  if(neImgBtn){
    neImgBtn.addEventListener('mousedown',function(e){e.preventDefault();});
    neImgBtn.addEventListener('click',function(){if(neImgInput)neImgInput.click();});
  }
  if(neImgInput){
    neImgInput.addEventListener('change',function(e){
      var file=e.target.files&&e.target.files[0];
      if(!file)return;
      if(file.size>5*1024*1024){showToast('图片过大(>5MB)，请选择更小的');e.target.value='';return;}
      var reader=new FileReader();
      reader.onload=function(ev){
        neCompressImg(ev.target.result,800,function(compressed){
          if(!compressed){showToast('图片处理失败');return;}
          rt.focus();neRestoreSel();
          document.execCommand('insertImage',false,compressed);
          // 默认图片块独占一行
          try{
            var sel=window.getSelection();
            if(sel&&sel.rangeCount){
              var node=sel.anchorNode;
              while(node&&node!==rt){if(node.nodeType===1&&node.tagName==='IMG')break;node=node.parentNode;}
              if(node&&node.tagName==='IMG'){
                var br=document.createElement('br');
                node.parentNode.insertBefore(br,node.nextSibling);
                var r=document.createRange();r.setStartAfter(br);r.collapse(true);
                sel.removeAllRanges();sel.addRange(r);
              }
            }
          }catch(e){}
          neSaveSel();rt.focus();
          showToast('图片已插入');
        });
      };
      reader.onerror=function(){showToast('读取图片失败');};
      reader.readAsDataURL(file);
      e.target.value='';
    });
  }

  // ===== V72: 语音转文字 =====
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var srInstance=null,srActive=false,neVoiceBtn=$('neVoiceBtn');
  if(neVoiceBtn){
    if(!SR){
      neVoiceBtn.classList.add('voice-unsupported');
      neVoiceBtn.title='当前浏览器不支持语音识别（请用 Chrome）';
    }
    neVoiceBtn.addEventListener('mousedown',function(e){e.preventDefault();});
    neVoiceBtn.addEventListener('click',function(){
      if(!SR){showToast('当前浏览器不支持语音识别，请用 Chrome 桌面/安卓版');return;}
      if(srActive){
        try{srInstance.stop();}catch(e){}
        srActive=false;
        neVoiceBtn.classList.remove('recording');
        neVoiceBtn.textContent='🎤';
        return;
      }
      try{
        srInstance=new SR();
        srInstance.lang='zh-CN';
        srInstance.continuous=true;
        srInstance.interimResults=true;
        var finalBuf='';
        srInstance.onresult=function(ev){
          var last=ev.results[ev.results.length-1];
          var text=last[0].transcript;
          if(last.isFinal){
            finalBuf+=text;
            rt.focus();neRestoreSel();
            document.execCommand('insertText',false,text);
            neSaveSel();
          }
        };
        srInstance.onerror=function(ev){
          var err=ev.error||'unknown';
          showToast('语音识别失败: '+err+(err==='not-allowed'?'（请允许麦克风权限）':''));
          srActive=false;
          neVoiceBtn.classList.remove('recording');
          neVoiceBtn.textContent='🎤';
        };
        srInstance.onend=function(){
          srActive=false;
          neVoiceBtn.classList.remove('recording');
          neVoiceBtn.textContent='🎤';
        };
        srInstance.start();
        srActive=true;
        neVoiceBtn.classList.add('recording');
        neVoiceBtn.textContent='🔴';
        showToast('开始录音，点击 🔴 停止');
      }catch(e){
        showToast('启动语音识别失败: '+e.message);
      }
    });
  }

  // ===== V71: 分割线/emoji/待办 ====="""

assert old_emoji_start in src, "V71 emoji block not found"
src = src.replace(old_emoji_start, new_js_block, 1)
print("3. JS image+voice handlers: OK")

# ============ 4. doSync 策略：psNotes 大时跳过云同步但保留本地 ============
old_sync_limit = "if(body.length>60000){showToast('同步数据过大('+Math.round(body.length/1024)+'KB)，请先导出备份');saveSyncStatus({lastTry:ts,ok:false,msg:'数据过大'});syncing=false;return false;}"
new_sync_limit = (
    "if(body.length>60000){"
    "var psNotesSize=JSON.stringify(psNotes||[]).length;"
    "if(psNotesSize>40000){showToast('笔记图片较多('+Math.round(psNotesSize/1024)+'KB)，已保存本地但未上传云端');"
    "saveSyncStatus({lastTry:ts,ok:false,msg:'笔记过大未同步'});syncing=false;return true;}"
    "showToast('同步数据过大('+Math.round(body.length/1024)+'KB)，请先导出备份');saveSyncStatus({lastTry:ts,ok:false,msg:'数据过大'});syncing=false;return false;}"
)
assert old_sync_limit in src, "doSync limit block not found"
src = src.replace(old_sync_limit, new_sync_limit, 1)
print("4. doSync psNotes strategy: OK")

# ============ 5. APP_VERSION → 72 ============
src = src.replace("var APP_VERSION=71;", "var APP_VERSION=72;", 1)
print("5. APP_VERSION → 72: OK")

# ============ Write ============
open('index.html','w',encoding='utf-8').write(src)
print("\n=== V72 patch applied, +%d bytes ===" % (len(src)-len(orig)))