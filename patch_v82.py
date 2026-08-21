#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

f = 'C:/Users/92809/WorkBuddy/2026-08-19-23-27-21/english-sentences/index.html'
with open(f, 'r', encoding='utf-8') as fp:
    src = fp.read()

# ============ 1. 重写 buildSkuNoLabel ：含中文检测，确保第一段是中文产品名 ============
old = r'''function buildSkuNoLabel(p,sk,si){
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

new = r'''function buildSkuNoLabel(p,sk,si){
  // V82: 三段式【产品名称（含#变体）-规格-数量个】
  // 第一段：优先取含中文的字段作为产品名（避免 fallback 到英文 title/name）
  var cnRe=/[\u4e00-\u9fa5]/;
  var tStr=(p.title||'').trim(),nStr=(p.name||'').trim();
  var prodLabel='';
  if(tStr&&cnRe.test(tStr)) prodLabel=tStr;
  else if(nStr&&cnRe.test(nStr)) prodLabel=nStr;
  else if(tStr) prodLabel=tStr;
  else if(nStr) prodLabel=nStr;
  var fallbackSku=!prodLabel;
  // 第二段：规格，自动剥离 prodLabel / 产品名 / 变体前缀
  var skuLabel=(sk.name||'').trim()||(sk.skuNo||'').trim();
  if(!skuLabel) skuLabel='\u89c4\u683c'+(si+1);
  var rest=skuLabel;
  if(prodLabel){
    if(rest.indexOf(prodLabel)===0) rest=rest.slice(prodLabel.length);
    else{
      var hi=prodLabel.indexOf('#');
      var base=hi>-1?prodLabel.slice(0,hi).replace(/[\s]+$/,''):prodLabel;
      if(base&&rest.indexOf(base)===0) rest=rest.slice(base.length);
      if(hi>-1){
        var vari=prodLabel.slice(hi+1).replace(/^[\s]+|[\s]+$/g,'');
        if(vari){
          var stripped=rest.replace(/^[\-\s\.\:]+/,'');
          if(stripped.indexOf(vari)===0) rest=stripped.slice(vari.length).replace(/^[\-\s\.\:]+/,'');
          else rest=stripped;
        }
      }
    }
  }
  rest=rest.replace(/^[\-\s\.\:]+/,'').replace(/[\-\s\.]+$/,'');
  // 第三段：数量个（>0 才显示）
  var q=parseInt(sk.qty)||0;
  // 兜底：若无 prodLabel，用 skuLabel 作为产品名段
  if(fallbackSku){
    var fb=skuLabel;
    if(q>0) fb+='-'+q+'\u4e2a';
    return fb;
  }
  var label=prodLabel;
  if(rest) label+='-'+rest;
  if(q>0) label+='-'+q+'\u4e2a';
  return label;
}'''

cnt = src.count(old)
print('buildSkuNoLabel 匹配数=', cnt)
assert cnt == 1, f'期望 1 处，匹配 {cnt}'
src = src.replace(old, new)

# ============ 2. APP_VERSION 升 V82 ============
src = src.replace('var APP_VERSION=81;', 'var APP_VERSION=82;', 1)

with open(f, 'w', encoding='utf-8') as fp:
    fp.write(src)

print('patch_v82.py 改动成功')
