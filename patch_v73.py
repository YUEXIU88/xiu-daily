# -*- coding: utf-8 -*-
"""V73: 修复 Shopee 产品图片刷新丢失问题
根因: V67 saveData 保存 spProducts 时去掉了 img 字段, 导致图片只存在内存中, 刷新即丢
修复: 把图片单独存到 localStorage 独立 key (xiu_sp_imgs_v1), saveData 剥离时同时存, loadAllData 恢复
"""
import sys

f = 'index.html'
src = open(f, 'r', encoding='utf-8').read()

# ============ 1. SK 增加 spImgs key ============
old_sk = "  interviewCustom:'xiu_interview_v1',\n  userLevel:'xiu_user_level_v1'\n};"
new_sk = "  interviewCustom:'xiu_interview_v1',\n  userLevel:'xiu_user_level_v1',\n  spImgs:'xiu_sp_imgs_v1'\n};"
assert old_sk in src, "SK block not found"
src = src.replace(old_sk, new_sk, 1)
print("1. SK.spImgs added")

# ============ 2. saveData: 剥离 img 时同时存到独立 key ============
old_save = "function saveData(key,val){try{var toSave=val;if(key===SK.spProducts&&Array.isArray(val)){toSave=val.map(function(p){var c={};for(var k in p){if(k!=='img')c[k]=p[k];}c.skus=(p.skus||[]).map(function(s){var cs={};for(var k2 in s){if(k2!=='img')cs[k2]=s[k2];}return cs;});return c;});}localStorage.setItem(key,JSON.stringify(toSave));}catch(e){console.warn('saveData failed:',key,e);showToast('\\u5b58\\u50a8\\u7a7a\\u95f4\\u4e0d\\u8db3');}}"

new_save = "function saveData(key,val){try{var toSave=val;if(key===SK.spProducts&&Array.isArray(val)){var imgMap={};toSave=val.map(function(p){var c={};for(var k in p){if(k!=='img')c[k]=p[k];else if(p.img)imgMap[p.id]=p.img;}c.skus=(p.skus||[]).map(function(s){var cs={};for(var k2 in s){if(k2!=='img')cs[k2]=s[k2];}return cs;});return c;});try{localStorage.setItem(SK.spImgs,JSON.stringify(imgMap));}catch(eImg){console.warn('spImgs save failed',eImg);}}localStorage.setItem(key,JSON.stringify(toSave));}catch(e){console.warn('saveData failed:',key,e);showToast('\\u5b58\\u50a8\\u7a7a\\u95f4\\u4e0d\\u8db3');}}"

assert old_save in src, "saveData block not found"
src = src.replace(old_save, new_save, 1)
print("2. saveData: images saved to separate key when stripping")

# ============ 3. loadAllData: 加载完产品后恢复图片 ============
old_load_end = "  interviewCustom=loadData(SK.interviewCustom,[]);userLevel=loadData(SK.userLevel,'A2');\n}"
new_load_end = "  interviewCustom=loadData(SK.interviewCustom,[]);userLevel=loadData(SK.userLevel,'A2');\n  try{var _imgs=JSON.parse(localStorage.getItem(SK.spImgs)||'{}');if(_imgs&&typeof _imgs==='object'){spProducts.forEach(function(p){if(!p.img&&_imgs[p.id])p.img=_imgs[p.id];});}}catch(e){console.warn('loadProductImgs failed',e);}\n}"

assert old_load_end in src, "loadAllData end not found"
src = src.replace(old_load_end, new_load_end, 1)
print("3. loadAllData: images restored from separate key")

# ============ 4. pagehide: 也保存图片 ============
old_pagehide = "if(window._spSaveTimer){clearTimeout(window._spSaveTimer);saveData(SK.spProducts,spProducts);}if(window._spDiscTimer){clearTimeout(window._spDiscTimer);saveData(SK.spProducts,spProducts);}"
new_pagehide = "if(window._spSaveTimer){clearTimeout(window._spSaveTimer);saveData(SK.spProducts,spProducts);}if(window._spDiscTimer){clearTimeout(window._spDiscTimer);saveData(SK.spProducts,spProducts);}try{var _ihm={};spProducts.forEach(function(p){if(p.img)_ihm[p.id]=p.img;});localStorage.setItem(SK.spImgs,JSON.stringify(_ihm));}catch(e){}"

assert old_pagehide in src, "pagehide not found"
src = src.replace(old_pagehide, new_pagehide, 1)
print("4. pagehide: images also saved")

# ============ 5. APP_VERSION 升级 ============
old_ver = "var APP_VERSION=72;"
new_ver = "var APP_VERSION=73;"
assert old_ver in src, "APP_VERSION not found"
src = src.replace(old_ver, new_ver, 1)
print("5. APP_VERSION -> 73")

# ============ 6. collectAllData: 也带上 spImgs map (让云同步也能恢复) ============
old_collect_end = "return{v:18,userSentences:userSentences"
new_collect_end = "var _imgMap={};(spProducts||[]).forEach(function(p){if(p.img)_imgMap[p.id]=_hashShort(p.img);});return{v:18,userSentences:userSentences"

assert old_collect_end in src, "collectAllData return not found"
src = src.replace(old_collect_end, new_collect_end, 1)
print("6. collectAllData: imgMap computed inline")

open(f, 'w', encoding='utf-8').write(src)
print("\nAll patches applied successfully!")
print("File size:", len(src), "bytes")
