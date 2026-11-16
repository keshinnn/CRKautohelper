'use strict';
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path');
let JSDOM; try { ({ JSDOM } = require('jsdom')); } catch { ({ JSDOM } = require('F:/CRK helper/node_modules/jsdom')); }

function page() {
  const dom = new JSDOM(`<nav class="nav"><button data-page="overview">o</button><button data-page="roster">r</button></nav>
   <section id="overview"><div class="stats"><div id="status"></div><div id="progress"></div><div id="floor"></div></div>
   <div class="grid"><article><span id="gamePreviewStatus"></span><img id="gamePreviewImage"></article><article class="card"><button id="run"></button></article></div></section>
   <section id="roster"></section><div id="toast"></div>`, { url: 'http://localhost', runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window; const calls = []; let tick;
  w.eval(`var authState={authenticated:true},activePage='overview',dirty=false;
   function $(id){return document.getElementById(id)}
   function el(t,c,x){const n=document.createElement(t);if(c)n.className=c;if(x!==undefined)n.textContent=x;return n}
   function guard(fn){return async(...a)=>{try{await fn(...a)}catch(e){window.lastError=e.message}}}
   function button(t,fn,c='btn'){const b=el('button',c,t);b.type='button';b.onclick=guard(fn);return b}
   function toast(t){window.toasts=(window.toasts||[]).concat(t)}
   function selectPage(p){activePage=p}
   var persist=async()=>{window.persisted=(window.persisted||0)+1};
   var api=async(...a)=>window.mockApi(...a);`);
  w.setInterval = fn => { tick = fn; return 1; }; w.setTimeout = fn => { fn(); return 1; };
  return { w, calls, tick: () => tick() };
}

test('自動通關卡：未就緒顯示原因且不能開始；就緒可開始；模擬卡隱藏', async () => {
  const { w, calls, tick } = page();
  let status = { mode: 'idle', running: false, ready: false, errors: ['區域 1・第 1 層：尚未選角'], warnings: [], zone: null, step: 0 };
  w.mockApi = async (url, method = 'GET', body) => { calls.push({ url, method, body }); if (url === '/api/bot/status') return status; if (url === '/api/bot/log') return []; return { ok: true }; };
  w.eval(fs.readFileSync(path.join(__dirname, '../web/bot-runner.js'), 'utf8'));
  await tick(); const d = w.document;
  assert.equal(d.getElementById('run').closest('article').hidden, true);
  const start = [...d.querySelectorAll('#botRunner button')].find(b => /開始自動通關/.test(b.textContent));
  assert.equal(start.disabled, true);
  assert.match(d.querySelector('.bot-problems').textContent, /尚未選角/);
  assert.equal(d.querySelector('.bot-message').getAttribute('aria-live'), 'polite');
  status = { ...status, ready: true, errors: [] }; await tick();
  assert.equal(start.disabled, false);
  await start.onclick();
  const s = calls.find(c => c.url === '/api/bot/start'); assert.deepEqual(JSON.parse(JSON.stringify(s.body)), { reset: false });
});

test('自動通關卡：手動關卡顯示接手區塊，按鈕送出交還；停止與鎖定', async () => {
  const { w, calls, tick } = page();
  let status = { mode: 'manual', running: true, ready: true, errors: [], warnings: [], zone: 4, step: 1, message: '手動關卡', manual: { zone: 4, floor: 2, note: '用薄荷醇' }, frame: true, n: 12 };
  w.mockApi = async (url, method = 'GET', body) => { calls.push({ url, method, body }); if (url === '/api/bot/status') return status; if (url === '/api/bot/log') return []; return { ok: true }; };
  w.eval(fs.readFileSync(path.join(__dirname, '../web/bot-runner.js'), 'utf8'));
  await tick(); const d = w.document;
  const hand = d.querySelector('.bot-handover');
  assert.equal(hand.hidden, false); assert.match(hand.textContent, /區域 4・第 2 層/); assert.match(hand.textContent, /用薄荷醇/);
  assert.match((w.toasts || []).join(), /手動關卡/);
  assert.match(d.getElementById('gamePreviewImage').src, /\/api\/bot\/frame\?n=12/);
  assert.equal(d.getElementById('progress').textContent, '區域 4');
  await hand.querySelector('button').onclick();
  assert.ok(calls.some(c => c.url === '/api/bot/resume' && c.method === 'POST'));
  status = { mode: 'paused', running: false, ready: true, errors: [], warnings: [], zone: 4, step: 1, halt: '區域4 第2步 已失敗 2 次', message: '鎖定' }; await tick();
  assert.equal(hand.hidden, true);
  const haltBox = d.querySelector('.bot-halt'); assert.equal(haltBox.hidden, false);
  const stop = [...d.querySelectorAll('#botRunner button')].find(b => b.textContent === '停止'); assert.equal(stop.disabled, true);
  await haltBox.querySelector('button').onclick();
  assert.ok(calls.some(c => c.url === '/api/bot/clear-halt'));
});

test('遊戲內角色卡片：已確認／舊版對應／待確認新卡片，確認送出角色', async () => {
  const { w, calls } = page();
  w.eval(`var C={characters:[{id:'osm',name:'金桂 / Golden Osmanthus Cookie'},{id:'x',name:'神秘 / Mystery Cookie'},{id:'y',name:'其他 / Other'}],initialRoster:['osm','x'],extraRoster:[]};`);
  w.mockApi = async (url, method = 'GET', body) => {
    calls.push({ url, method, body });
    if (url === '/api/bot/status') return { mode: 'idle', running: false, ready: true, errors: [], warnings: [] };
    if (url === '/api/bot/cards' && method === 'GET') return { labels: ['氣泡'], roster: [{ id: 'osm', name: '金桂 / Golden Osmanthus Cookie', inBank: true, card: 'osm', how: 'bank' }, { id: 'x', name: '神秘', inBank: false, card: null, how: 'none' }],
      inbox: [{ file: '0123456789abcdef.png', suggestions: [{ id: 'y', name: '其他', similarity: 0.71 }] }] };
    return { ok: true, map: {} };
  };
  w.eval(fs.readFileSync(path.join(__dirname, '../web/bot-runner.js'), 'utf8'));
  w.document.querySelector('[data-page="roster"]').dispatchEvent(new w.Event('click', { bubbles: true }));
  for (let i = 0; i < 4; i++) await new Promise(r => setImmediate(r));
  const d = w.document, rows = d.querySelectorAll('#botCards .bot-card-row');
  assert.equal(rows.length, 2);
  assert.match(rows[0].textContent, /已確認/); assert.match(rows[0].querySelector('img').src, /bank-image\/osm/);
  assert.match(rows[1].textContent, /需要遊戲內卡片/);
  const item = d.querySelector('.bot-inbox-item'); assert.ok(item);
  const sel = item.querySelector('select'); assert.equal(sel.querySelector('optgroup').label, '模型判定與相似角色');
  assert.equal(sel.value, '');   // never preselects a model guess
  const ok = [...item.querySelectorAll('button')].find(b => b.textContent === '確認');
  await ok.onclick(); assert.match(w.lastError || '', /請先選擇角色/);
  sel.value = 'y'; await ok.onclick();
  const c = calls.find(c => c.url === '/api/bot/inbox/confirm'); assert.deepEqual(JSON.parse(JSON.stringify(c.body)), { file: '0123456789abcdef.png', characterId: 'y' });
});
