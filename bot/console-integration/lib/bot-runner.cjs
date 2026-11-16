'use strict';
// Bridge between the CRK helper web console and the MuMu runner (bot/runner.py).
// - toStrategy(): the console's saved config (web/config.js schema) -> runner strategy JSON.
// - BotRunner: start / stop / hand-back / clear-halt, status, latest frame, log tail.
// The runner owns all game input; this module only starts it and reads what it writes.
const fs = require('node:fs'), path = require('node:path'), { spawn } = require('node:child_process');

const EVENT = { auto: 'random', battle: 'battle', heal: 'heal', boss: 'boss' };

function chineseName(name) { return String(name || '').split(' / ')[0].replace(/餅乾$/, '').trim(); }

// card label (bot/cards/labels.json key) for a console character: explicit map first, then a unique name match.
function suggestCard(character, labels) {
  const n = chineseName(character.name);
  // exact names only: '氣泡飲' must not silently become the '氣泡' card (a wrong identity is worse than asking)
  return labels.includes(n) ? n : null;
}

function cardFor(character, labels, map, bank = {}) {
  if (bank[character.id]) return { card: character.id, how: 'bank' };   // confirmed in-game card (bot/cards/bank.json)
  if (map[character.id] && labels.includes(map[character.id])) return { card: map[character.id], how: 'map' };
  const s = suggestCard(character, labels);
  return s ? { card: s, how: 'name' } : { card: null, how: 'none' };
}

function toStrategy(config, { labels = [], map = {}, treasureNames = null, bank = {} } = {}) {
  const errors = [], warnings = [];
  const chars = new Map(config.characters.map(c => [c.id, c]));
  const trs = new Map(config.treasures.map(t => [t.id, t.name]));
  const known = treasureNames ? new Set(treasureNames) : null;
  const tname = id => { const n = trs.get(id); if (known && n && !known.has(n)) warnings.push(`寶物「${n}」不在辨識清單，裝備時會改用讀標題逐一尋找`); return n; };
  const zones = [];
  const { startZone, endZone } = config.options;
  for (const z of config.zones) {
    if (z.number < startZone || z.number > endZone) continue;
    const steps = z.levels.map((l, i) => {
      const where = `區域 ${z.number}・${l.event === 'boss' ? '王關' : '第 ' + (i + 1) + ' 層'}`;
      const step = { type: EVENT[l.event] || 'random', column: l.event === 'boss' ? null : l.route };
      if (l.manualPlay) { step.manual = true; if (l.manualPlayNotes) step.note = l.manualPlayNotes; }
      if (l.event !== 'heal') {
        const team = [];
        for (const t of l.team) {
          const c = chars.get(t.characterId); if (!c) continue;
          const { card } = cardFor(c, labels, map, bank);
          if (card) team.push(card); else if (!l.manualPlay) errors.push(`${where}：「${c.name}」還沒有對應的角色卡片`);
        }
        if (!l.team.length && !l.manualPlay) errors.push(`${where}：尚未選角（或勾選「本關由玩家手動遊玩」）`);
        if (team.length) step.team = team;
        if (l.treasures.length) step.treasures = l.treasures.map(tname).filter(Boolean);
      }
      return step;
    });
    zones.push({ zone: z.number, steps });
  }
  const def = (config.defaultTreasures || []).map(tname).filter(Boolean);
  if (def.length && def.length < 3) warnings.push('預設寶物未選滿三件');
  const strategy = {
    format: 'crk-belowland-strategy', version: 1,
    meta: { title: config.meta.name, source: 'crk-helper console config' },
    treasures: { default: def },
    options: { retryLimit: config.options.infiniteRetry ? 99 : 0, ignoreMissingEquipment: true },
    zones,
  };
  return { strategy, errors, warnings: [...new Set(warnings)] };
}

class BotRunner {
  constructor({ root, python = process.env.CRK_PYTHON, spawnFn = spawn, now = Date.now } = {}) {
    this.root = root; this.bot = path.join(root, 'bot'); this.now = now; this.spawnFn = spawnFn;
    this.python = python || (fs.existsSync(path.join(root, '.venv', 'Scripts', 'python.exe')) ? path.join(root, '.venv', 'Scripts', 'python.exe') : 'python');
    this.proc = null; this.logFile = null;
  }
  p(...a) { return path.join(this.bot, ...a); }
  read(file, d) { try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return d; } }
  labels() { return Object.keys(this.read(this.p('cards', 'labels.json'), {})); }
  cardMap() { return this.read(this.p('cards', 'character-map.json'), {}); }
  saveCardMap(map) {
    const labels = this.labels(), clean = {};
    for (const [id, card] of Object.entries(map || {})) {
      if (!/^[a-zA-Z0-9_-]{1,80}$/.test(id)) throw new Error('角色識別碼不正確');
      if (card === '' || card === null) continue;
      if (!labels.includes(card)) throw new Error(`沒有「${card}」這張角色卡片`);
      clean[id] = card;
    }
    fs.writeFileSync(this.p('cards', 'character-map.json'), JSON.stringify(clean, null, 1));
    return clean;
  }
  cardImage(label) {
    const file = this.read(this.p('cards', 'labels.json'), {})[label];
    return file && /^[\w-]+\.png$/.test(file) ? this.p('cards', file) : null;
  }
  treasureNames() {
    const m = this.read(path.join(this.root, 'data', 'treasures', 'manifest.json'), { treasures: [] });
    return m.treasures.map(t => t.name);
  }
  plan(config) { return toStrategy(config, { labels: this.labels(), map: this.cardMap(), treasureNames: this.treasureNames(), bank: this.bank() }); }
  // ---- confirmed card bank + inbox of unknown cards seen in the game ----
  bank() { return (this.read(this.p('cards', 'bank.json'), { cards: {} }).cards) || {}; }
  bankImage(id) {
    const row = this.bank()[id]; const f = row && row.files && row.files[0] && row.files[0].file;
    return f && /^bank\/[\w.-]+\.png$/.test(f) ? this.p('cards', f) : null;
  }
  inbox() {
    const dir = this.p('cards', 'inbox'); if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir).filter(f => /^[0-9a-f]{16}\.png$/.test(f)).map(f => {
      const meta = this.read(path.join(dir, f.replace(/\.png$/, '.json')), null);
      return { file: f, at: fs.statSync(path.join(dir, f)).mtimeMs, suggestions: meta ? meta.suggestions : null,
        modelId: meta ? meta.modelId || null : null, modelReason: meta ? meta.reason || '' : '' };
    }).sort((a, b) => b.at - a.at);
  }
  inboxImage(file) { return /^[0-9a-f]{16}\.png$/.test(file) && fs.existsSync(this.p('cards', 'inbox', file)) ? this.p('cards', 'inbox', file) : null; }
  confirmCard(file, character) {
    if (this.running()) throw new Error('請先停止自動通關再確認卡片');
    const src = this.inboxImage(file); if (!src) throw new Error('找不到這張卡片');
    if (!character || !/^[a-zA-Z0-9_-]{1,80}$/.test(character.id)) throw new Error('請選擇角色');
    const data = this.read(this.p('cards', 'bank.json'), { format: 'crk-mumu-card-bank-v1', cards: {} }); data.cards = data.cards || {};
    fs.mkdirSync(this.p('cards', 'bank'), { recursive: true });
    const rel = `bank/${character.id}-${file}`; fs.copyFileSync(src, this.p('cards', rel));
    const row = data.cards[character.id] || { name: chineseName(character.name), english: String(character.name).split(' / ')[1] || '', aliases: [], files: [] };
    row.files.push({ file: rel, source: 'MuMu team strip, unknown-card inbox', confirmedBy: 'user in console ' + new Date(this.now()).toISOString().slice(0, 10) });
    data.cards[character.id] = row;
    fs.writeFileSync(this.p('cards', 'bank.json'), JSON.stringify(data, null, 1));
    this.moveOut(file, 'confirmed'); return { ok: true, id: character.id };
  }
  dismissCard(file) { if (!this.inboxImage(file)) throw new Error('找不到這張卡片'); this.moveOut(file, 'dismissed'); return { ok: true }; }
  moveOut(file, sub) {
    const dir = this.p('cards', 'inbox'), to = path.join(dir, sub); fs.mkdirSync(to, { recursive: true });
    for (const f of [file, file.replace(/\.png$/, '.json')]) if (fs.existsSync(path.join(dir, f))) fs.renameSync(path.join(dir, f), path.join(to, f));
  }
  suggest() {
    if (this.suggesting && this.suggesting.exitCode === null) return { ok: true, running: true };
    this.suggesting = this.spawnFn(this.python, ['-B', this.p('card_suggest.py')], { cwd: this.root, stdio: 'ignore', windowsHide: true, env: { ...process.env, PYTHONUTF8: '1' } });
    return { ok: true, running: true };
  }
  running() {
    if (this.proc && this.proc.exitCode === null && !this.proc.killed) return true;
    const s = this.read(this.p('status.json'), {});   // a runner started elsewhere (agent / bot/webui.py)
    return ['auto', 'manual'].includes(s.mode) && this.now() / 1000 - (s.at || 0) < 45;
  }
  status(config) {
    const s = this.read(this.p('status.json'), {}), run = this.read(this.p('run-state.json'), {});
    const age = s.at ? Math.round(this.now() / 1000 - s.at) : null;
    const running = this.running();
    const mode = running ? (s.mode === 'manual' ? 'manual' : 'auto') : (['paused', 'error', 'stopped'].includes(s.mode) ? s.mode : 'idle');
    const out = { mode, running, message: s.message || '', screen: s.state || '', age, zone: run.zone ?? null, step: run.step ?? null,
      halt: run.halt || '', manual: run.manual || null, frame: s.frame ? true : false, n: s.n || 0 };
    if (config) {
      const p = this.plan(config); out.ready = !p.errors.length; out.errors = p.errors.slice(0, 8); out.warnings = p.warnings.slice(0, 5);
      const z = p.strategy.zones.find(z => z.zone === (out.zone || config.options.startZone));
      out.route = z ? { zone: z.zone, floors: z.steps.map((s, i) => ({ floor: i + 1, type: s.type, manual: !!s.manual,
        state: out.zone === z.zone ? (i < (out.step || 0) ? 'done' : i === (out.step || 0) ? 'current' : 'next') : 'next' })) } : null;
    }
    return out;
  }
  start(config, { reset = false } = {}) {
    if (this.running()) throw new Error('自動通關已經在執行中');
    const { strategy, errors } = this.plan(config);
    if (errors.length) throw new Error('攻略還不能自動執行：' + errors.slice(0, 3).join('；'));
    const file = path.join(this.root, 'runtime', 'runner-strategy.json');
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(strategy, null, 1));
    if (reset) fs.writeFileSync(this.p('run-state.json'), '{"zone": null, "step": 0, "pending": null}');
    fs.mkdirSync(this.p('runs'), { recursive: true });
    this.logFile = this.p('runs', 'console-' + new Date(this.now()).toISOString().replace(/[:.]/g, '-') + '.log');
    const out = fs.openSync(this.logFile, 'w');
    this.proc = this.spawnFn(this.python, ['-B', this.p('runner.py'), file, '--steps', '100000'],
      { cwd: this.root, stdio: ['ignore', out, out], windowsHide: true, env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' } });
    fs.writeFileSync(this.p('status.json'), JSON.stringify({ mode: 'auto', message: '啟動中', at: this.now() / 1000 }));
    return { ok: true, zones: strategy.zones.length };
  }
  touch(name) { fs.mkdirSync(this.p('jobs'), { recursive: true }); fs.writeFileSync(this.p('jobs', name), String(this.now())); }
  stop() { this.touch('STOP_RUN'); return { ok: true }; }
  resume() { if (this.status().mode !== 'manual') throw new Error('目前不是手動關卡'); this.touch('RESUME'); return { ok: true }; }
  clearHalt() {
    if (this.running()) throw new Error('請先停止自動通關');
    const st = this.read(this.p('run-state.json'), {}); delete st.halt; delete st.failures;
    fs.writeFileSync(this.p('run-state.json'), JSON.stringify(st, null, 1)); return { ok: true };
  }
  frameFile() {
    const f = this.read(this.p('status.json'), {}).frame;
    if (!f) return null;
    const abs = path.resolve(f), runs = path.resolve(this.p('runs'));
    return abs.startsWith(runs + path.sep) && fs.existsSync(abs) ? abs : null;
  }
  log(lines = 40) {
    let file = this.logFile;
    if (!file || !fs.existsSync(file)) {
      const dir = this.p('runs'); if (!fs.existsSync(dir)) return [];
      const logs = fs.readdirSync(dir).filter(f => /\.log$/.test(f)).map(f => path.join(dir, f)).sort((a, b) => fs.statSync(a).mtimeMs - fs.statSync(b).mtimeMs);
      file = logs.pop(); if (!file) return [];
    }
    const rows = fs.readFileSync(file, 'utf8').split(/\r?\n/).filter(Boolean).slice(-lines * 3);
    const out = [];
    for (const r of rows) {
      try { const j = JSON.parse(r); if (j.action) out.push({ n: j.n, kind: j.action[0], text: String(j.action[j.action.length - 1]) }); }
      catch { if (!/^\s+File |^Traceback|^\s+\^/.test(r)) out.push({ kind: 'note', text: r.trim() }); }
    }
    return out.slice(-lines);
  }
}

module.exports = { toStrategy, BotRunner, suggestCard, cardFor, chineseName };
