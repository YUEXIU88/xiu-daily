const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf-8');
const start = html.indexOf('function buildSkuNoLabel(p,sk,si){');
// 数大括号深度
let i = html.indexOf('{', start), depth = 1, end = i;
for (let j = i + 1; j < html.length; j++) {
  if (html[j] === '{') depth++;
  else if (html[j] === '}') { depth--; if (depth === 0) { end = j; break; } }
}
const fnSrc = html.substring(start, end + 1);
// 写到临时文件
fs.writeFileSync('_fn_tmp.js', 'function buildSkuNoLabel(p,sk,si){' + fnSrc.substring(fnSrc.indexOf('{')+1, fnSrc.lastIndexOf('}')) + '\n}\n' +
'module.exports = buildSkuNoLabel;');
const buildSkuNoLabel = require('./_fn_tmp.js');

const cases = [
  // 用户的真实数据：title=中文+变体，name=英文
  [{title:'豆浆过滤网 #100目', name:'5PCS Reusable Nylon Filter Bags For Soy Milk Wine Yogurt'},
   {name:'15x20', qty:1}, '豆浆过滤网 #100目-15x20-1个'],
  [{title:'豆浆过滤网 #100目', name:'5PCS Reusable Nylon Filter Bags...'},
   {name:'20x30', qty:100}, '豆浆过滤网 #100目-20x30-100个'],
  // 中文在 name
  [{title:'5PCS Filter', name:'豆浆过滤网 #100目'},
   {name:'15x20', qty:1}, '豆浆过滤网 #100目-15x20-1个'],
  // 旧 SKU.name 带产品名前缀
  [{title:'豆浆过滤网 #100目', name:'豆浆过滤网'},
   {name:'豆浆过滤网-100目-15x20', qty:1}, '豆浆过滤网 #100目-15x20-1个'],
  // qty=0
  [{title:'豆浆过滤网 #100目', name:'豆浆过滤网'},
   {name:'15x20', qty:0}, '豆浆过滤网 #100目-15x20'],
  // 全英文
  [{title:'SPCS Filter Bags', name:'SPCS Filter Bags'},
   {name:'20x30', qty:1}, 'SPCS Filter Bags-20x30-1个'],
  // 全空 兜底
  [{title:'', name:''},
   {name:'15x20', qty:1}, '15x20-1个'],
  // 单字产品
  [{title:'滤网 #100', name:'滤网'},
   {name:'100目', qty:50}, '滤网 #100-100目-50个'],
];

let pass = 0;
cases.forEach((c, i) => {
  const r = buildSkuNoLabel(c[0], c[1], 0);
  const ok = r === c[2];
  pass += ok ? 1 : 0;
  console.log((ok ? 'PASS' : 'FAIL') + ' case' + (i + 1) + ': got=' + JSON.stringify(r) +
    (ok ? '' : '  exp=' + JSON.stringify(c[2])));
});
console.log('\nUnit:', pass + '/' + cases.length, 'passed');
try { fs.unlinkSync('_fn_tmp.js'); } catch(e){}
