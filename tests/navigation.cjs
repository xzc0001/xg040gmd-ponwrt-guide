const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('docs/index.html','utf8');
const js=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const g=vm.runInNewContext(js+'; Guide',{}, {timeout:3000});
let id=g.next('start'),seen=[];while(id){seen.push(id);assert(seen.length<=19);id=g.next(id)}
assert.equal(seen.length,19);assert.equal(seen.at(-1),'acceptance');
assert.equal(g.next('verify-backup'),'ready');assert.equal(g.next('uboot'),'fip');assert.equal(g.next('fip'),'board-data');assert.equal(g.next('board-data'),'system');
assert(g.advice({...g.empty().conditions,pon:'gpon'}).some(a=>a.hold));
assert(g.advice({...g.empty().conditions,backup:'fail'}).some(a=>a.hold));
const s=g.clean({done:['fip','fip','invalid'],password:'discard'});assert.equal(s.done.length,1);assert(!('password' in s));
assert(g.search('USB_READY').some(r=>r.id==='usb-backup'));assert.equal(g.fault(''),null);
console.log('PASS: full navigation, write order, stops, state sanitization and search');
