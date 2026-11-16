'use strict';
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const Schema = require('../web/config.js');
const { toStrategy, BotRunner, suggestCard } = require('../lib/bot-runner.cjs');

const LABELS = ['金桂', '薄荷醇', '風鈴草', '氣泡', '奶油蘇打'];
function sampleConfig() {
  const c = Schema.defaults();
  c.characters = [
    { id: 'osm', name: '金桂 / Golden Osmanthus Cookie', skins: [], builds: [] },
    { id: 'men', name: '薄荷醇 / Menthol Cookie', skins: [], builds: [] },
    { id: 'bell', name: '風鈴草 / Silverbell Cookie', skins: [], builds: [] },
    { id: 'soda', name: '氣泡水 / Cream Soda Cookie', skins: [], builds: [] },
  ];
  c.initialRoster = ['osm', 'men', 'bell', 'soda'];
  c.treasures = [{ id: 't1', name: '老朝聖者的致勝秘笈', image: '' }, { id: 't2', name: '蘊含紅色魔力的哨子', image: '' }, { id: 't3', name: '做夢熊熊果凍的閃爍果凍鐘錶', image: '' }];
  c.defaultTreasures = ['t1', 't2', 't3'];
  c.options.startZone = 1; c.options.endZone = 2;
  const z1 = c.zones[0].levels;
  z1[0].team = [{ characterId: 'osm', buildId: '' }];
  z1[1].team = [{ characterId: 'men', buildId: '' }];
  z1[1].manualPlay = true; z1[1].manualPlayNotes = '這層需手動';
  z1[2].event = 'heal';
  z1[3].team = [{ characterId: 'bell', buildId: '' }, { characterId: 'osm', buildId: '' }];
  z1[3].treasures = ['t2'];
  z1[4].team = [{ characterId: 'osm', buildId: '' }];
  for (const l of c.zones[1].levels) l.team = [{ characterId: 'men', buildId: '' }];
  return Schema.validate(c);
}

test('攻略轉換：事件、路線、手動關卡、寶物、區域範圍', () => {
  const { strategy, errors } = toStrategy(sampleConfig(), { labels: LABELS, map: { soda: '奶油蘇打' } });
  assert.deepEqual(errors, []);
  assert.deepEqual(strategy.zones.map(z => z.zone), [1, 2]);
  const s = strategy.zones[0].steps;
  assert.deepEqual(s[0], { type: 'random', column: 2, team: ['金桂'] });
  assert.equal(s[1].manual, true); assert.equal(s[1].note, '這層需手動');
  assert.equal(s[2].type, 'heal'); assert.equal(s[2].team, undefined);
  assert.deepEqual(s[3].team, ['風鈴草', '金桂']); assert.deepEqual(s[3].treasures, ['蘊含紅色魔力的哨子']);
  assert.deepEqual(s[4], { type: 'boss', column: null, team: ['金桂'] });
  assert.deepEqual(strategy.treasures.default, ['老朝聖者的致勝秘笈', '蘊含紅色魔力的哨子', '做夢熊熊果凍的閃爍果凍鐘錶']);
  assert.equal(strategy.options.retryLimit, 99);
});

test('角色卡片：名稱模糊時不猜，需明確對應；手動關卡不要求隊伍', () => {
  assert.equal(suggestCard({ name: '金桂 / Golden Osmanthus Cookie' }, LABELS), '金桂');
  assert.equal(suggestCard({ name: '阿福花餅乾 / Asphodel Cookie' }, ['阿福花']), '阿福花');
  assert.equal(suggestCard({ name: '氣泡飲 / Sparkling Cookie' }, LABELS), null);   // partial name -> ask, never guess
  const c = sampleConfig(); c.characters.push({ id: 'x', name: '神秘 / Mystery Cookie', skins: [], builds: [] }); c.initialRoster.push('x');
  c.zones[0].levels[0].team = [{ characterId: 'x', buildId: '' }];
  let r = toStrategy(c, { labels: LABELS, map: { soda: '奶油蘇打' } });
  assert.match(r.errors.join(), /神秘.*還沒有對應的角色卡片/);
  r = toStrategy(c, { labels: LABELS, map: { x: '奶油蘇打', soda: '氣泡' } });
  assert.deepEqual(r.errors, []); assert.deepEqual(r.strategy.zones[0].steps[0].team, ['奶油蘇打']);
  c.zones[0].levels[0].team = []; c.zones[0].levels[0].manualPlay = true;
  assert.deepEqual(toStrategy(c, { labels: LABELS, map: { soda: '氣泡' } }).errors, []);
});

function tempRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'crk-bot-'));
  fs.mkdirSync(path.join(root, 'bot', 'cards'), { recursive: true });
  fs.writeFileSync(path.join(root, 'bot', 'cards', 'labels.json'), JSON.stringify(Object.fromEntries(LABELS.map((l, i) => [l, `card${i}.png`]))));
  fs.writeFileSync(path.join(root, 'bot', 'cards', 'card0.png'), Buffer.from([0x89, 0x50, 0x4e, 0x47]));
  return root;
}

test('BotRunner：啟動寫出攻略並帶正確參數；交還與鎖定的前提', () => {
  const root = tempRoot(), calls = [];
  const fake = (cmd, args, opts) => { calls.push({ cmd, args, opts }); return { exitCode: null, killed: false }; };
  const b = new BotRunner({ root, python: 'py', spawnFn: fake, now: () => 1e12 });
  assert.equal(b.start(sampleConfig(), { reset: true }).ok, true);
  assert.equal(calls.length, 1); assert.equal(calls[0].cmd, 'py');
  const strat = JSON.parse(fs.readFileSync(calls[0].args[2], 'utf8'));
  assert.equal(strat.zones[0].steps[1].manual, true);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, 'bot', 'run-state.json'))), { zone: null, step: 0, pending: null });
  assert.throws(() => b.start(sampleConfig()), /已經在執行中/);
  assert.throws(() => b.resume(), /不是手動關卡/);
  assert.throws(() => b.clearHalt(), /先停止/);
  fs.writeFileSync(path.join(root, 'bot', 'status.json'), JSON.stringify({ mode: 'manual', message: 'm', at: 1e9 }));
  assert.equal(b.status().mode, 'manual');
  b.resume(); assert.ok(fs.existsSync(path.join(root, 'bot', 'jobs', 'RESUME')));
  b.stop(); assert.ok(fs.existsSync(path.join(root, 'bot', 'jobs', 'STOP_RUN')));
  assert.throws(() => b.saveCardMap({ osm: '不存在' }), /沒有「不存在」/);
  assert.deepEqual(b.saveCardMap({ osm: '金桂', men: '' }), { osm: '金桂' });
});

test('BotRunner：攻略有缺漏時拒絕啟動；畫面路徑只限 runs/', () => {
  const root = tempRoot(), b = new BotRunner({ root, python: 'py', spawnFn: () => ({ exitCode: null }) });
  const c = sampleConfig(); c.zones[0].levels[0].team = [];
  assert.throws(() => b.start(c), /還不能自動執行/);
  fs.writeFileSync(path.join(root, 'bot', 'status.json'), JSON.stringify({ mode: 'paused', frame: path.join(root, 'bot', 'cards', 'card0.png') }));
  assert.equal(b.frameFile(), null);
});

test('HTTP：/api/bot/* 需控制啟用，狀態含攻略檢查', async () => {
  const { createApp } = require('../server.cjs');
  const root = tempRoot(), data = fs.mkdtempSync(path.join(os.tmpdir(), 'crk-data-'));
  const calls = [];
  const bot = new BotRunner({ root, python: 'py', spawnFn: (...a) => { calls.push(a); return { exitCode: null, killed: false }; } });
  for (const enabled of [false, true]) {
    const { server } = createApp({ dataDir: data, controlEnabled: enabled, botRunner: bot });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    try {
    const base = `http://127.0.0.1:${server.address().port}`;
    const st = await (await fetch(base + '/api/bot/status')).json();
    assert.equal(typeof st.ready, 'boolean'); assert.ok(Array.isArray(st.errors));
    const r = await fetch(base + '/api/bot/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    if (!enabled) assert.equal(r.status, 409);
    else assert.ok([202, 400].includes(r.status));   // seeded config may or may not be complete
    bot.proc = null; fs.rmSync(path.join(root, 'bot', 'status.json'), { force: true });
    let cards = await (await fetch(base + '/api/bot/cards')).json();
    assert.deepEqual(cards.labels, LABELS);
    const put = await fetch(base + '/api/config', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sampleConfig()) });
    assert.equal(put.status, 200);
    cards = await (await fetch(base + '/api/bot/cards')).json();
    assert.deepEqual(cards.roster.map(r => [r.id, r.card, r.how]), [['osm', '金桂', 'name'], ['men', '薄荷醇', 'name'], ['bell', '風鈴草', 'name'], ['soda', null, 'none']]);
    const ok = await fetch(base + '/api/bot/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{"reset":true}' });
    if (enabled) { assert.equal(ok.status, 202, await ok.clone().text()); await fetch(base + '/api/bot/stop', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }); bot.proc = null; }
    assert.equal((await fetch(base + '/api/bot/card/' + encodeURIComponent('金桂'))).status, 200);
    assert.equal((await fetch(base + '/api/bot/card/' + encodeURIComponent('../x'))).status, 404);
    bot.proc = null; fs.rmSync(path.join(root, 'bot', 'status.json'), { force: true });
    if (enabled) {   // a cookie that is not in the catalog: the inbox creates it once (new id, saved config, name table)
      fs.mkdirSync(path.join(root, 'bot', 'cards', 'inbox'), { recursive: true }); fs.writeFileSync(path.join(root, 'bot', 'cards', 'inbox', '00112233445566aa.png'), 'z');
      const post = body => fetch(base + '/api/bot/inbox/confirm', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      assert.equal((await post({ file: '00112233445566aa.png', newName: '' })).status, 400);
      assert.equal((await post({ file: '00112233445566aa.png', newName: '金桂' })).status, 400, 'same name as an existing character');
      const made = await (await post({ file: '00112233445566aa.png', newName: '新來的餅乾' })).json();
      assert.match(made.created, /^cookie-\d{3}$/);
      const cfg = await (await fetch(base + '/api/config')).json();
      assert.ok(cfg.characters.some(c => c.id === made.created && c.name === '新來的餅乾'));
      assert.equal(bot.bank()[made.created].files.length, 1);
      assert.equal(JSON.parse(fs.readFileSync(path.join(root, 'data', 'name-overrides-tw.json'), 'utf8')).added[made.created].name, '新來的餅乾');
    }
    } finally { server.closeAllConnections?.(); await new Promise(r => server.close(r)); }
  }
});

test('卡片庫：已確認卡片優先，新卡片需使用者確認才入庫', () => {
  const root = tempRoot();
  const b = new BotRunner({ root, python: 'py', spawnFn: () => ({ exitCode: null }) });
  fs.writeFileSync(path.join(root, 'bot', 'cards', 'bank.json'), JSON.stringify({ cards: { soda: { name: '氣泡水', files: [{ file: 'bank/soda-s8.png' }] } } }));
  let r = toStrategy(sampleConfig(), { labels: LABELS, map: {}, bank: b.bank() });
  assert.deepEqual(r.errors, []);
  const c = sampleConfig(); c.zones[0].levels[0].team = [{ characterId: 'soda', buildId: '' }];
  r = toStrategy(c, { labels: LABELS, map: {}, bank: b.bank() }); assert.deepEqual(r.strategy.zones[0].steps[0].team, ['soda']);
  const inbox = path.join(root, 'bot', 'cards', 'inbox'); fs.mkdirSync(inbox, { recursive: true });
  fs.writeFileSync(path.join(inbox, '0123456789abcdef.png'), 'x'); fs.writeFileSync(path.join(inbox, 'fedcba9876543210.png'), 'y');
  assert.equal(b.inbox().length, 2);
  assert.throws(() => b.confirmCard('../x.png', { id: 'men', name: '薄荷醇 / Menthol Cookie' }), /找不到/);
  b.confirmCard('0123456789abcdef.png', { id: 'men', name: '薄荷醇 / Menthol Cookie' });
  assert.equal(b.bank().men.files[0].file, 'bank/men-0123456789abcdef.png');
  assert.ok(fs.existsSync(path.join(root, 'bot', 'cards', 'bank', 'men-0123456789abcdef.png')));
  b.dismissCard('fedcba9876543210.png'); assert.equal(b.inbox().length, 0);
  assert.equal(b.bankImage('men'), path.join(root, 'bot', 'cards', 'bank/men-0123456789abcdef.png'));
});

test('辨識模型可找卡的角色＝Codex 目錄＋擁有角色的遊戲內清單卡片', () => {
  const root = tempRoot(), b = new BotRunner({ root, python: 'py', spawnFn: () => ({ exitCode: null }) });
  fs.mkdirSync(path.join(root, 'models', 'cards'), { recursive: true });
  fs.writeFileSync(path.join(root, 'models', 'cards', 'model.json'), JSON.stringify({ classes: [{ id: 'cookie-001' }] }));
  fs.writeFileSync(path.join(root, 'bot', 'cards', 'owned.json'), JSON.stringify({ cards: { 'cookie-190': { name: '索尼克', files: [] } } }));
  assert.deepEqual([...b.modelIds()].sort(), ['cookie-001', 'cookie-190']);
});

test('沒有遊戲內卡片的角色：在辨識模型目錄內 → 交給模型（警告）；不在目錄內 → 擋下', () => {
  const c = sampleConfig();
  c.characters.push({ id: 'cookie-139', name: '甜辣醬餅乾 / Chili Pepper Cookie', skins: [], builds: [] }, { id: 'cookie-184', name: '氣泡水餅乾', skins: [], builds: [] });
  c.zones[0].levels[4].team = [{ characterId: 'cookie-139', buildId: '' }];
  c.zones[1].levels[0].team = [{ characterId: 'cookie-184', buildId: '' }];
  const cfg = Schema.validate(c);
  const r = toStrategy(cfg, { labels: LABELS, map: { soda: '奶油蘇打' }, modelIds: new Set(['cookie-139']) });
  assert.deepEqual(r.strategy.zones[0].steps[4].team, ['cookie-139']);
  assert.ok(r.warnings.some(w => w.includes('甜辣醬') && w.includes('辨識模型')));
  assert.deepEqual(r.errors, ['區域 2・第 1 層：「氣泡水餅乾」還沒有對應的角色卡片']);
  assert.ok(toStrategy(cfg, { labels: LABELS, map: { soda: '奶油蘇打' } }).errors.length === 2, 'without the model catalog both stay errors');
});
