const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf-8');
const re = /<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g;
let m, ok = 0, fail = 0;
while ((m = re.exec(html))) {
  try { new Function(m[1]); ok++; }
  catch (e) { fail++; console.log('Err:', e.message.slice(0, 200)); }
}
console.log('Scripts:', ok, 'ok,', fail, 'fail');
console.log('psLedger key:', html.includes("psLedger:'xiu_ps_ledger_v1'"));
console.log('psDebts key:', html.includes("psDebts:'xiu_ps_debts_v1'"));
console.log('debt module:', html.includes("MODULES['ps-debt']"));
console.log('ledger module:', html.includes("MODULES['ps-ledger']"));
console.log('disc under title:', html.includes('titleWrap+prodDiscInputs(p)'));
console.log('head flex:', html.includes('sp-tb-head'));
console.log('col-title td removed:', !html.includes('col-title\\">'));
console.log('colspan=5:', html.includes('colspan="5"'));
console.log('APP_VERSION=79:', html.includes('var APP_VERSION=79;'));
