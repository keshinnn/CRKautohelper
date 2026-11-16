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

function cardFor(character, labels, map) {
  if (map[character.id] && labels.includes(map[character.id])) return { card: map[character.id], how: 'map' };
  const s = suggestCard(character, labels);
  return s ? { card: s, how: 'name' } : { card: null, how: 'none' };
}

function toStrategy(config, { labels = [], map = {}, treasureNames = null } = {}) {
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
          const { card } = cardFor(c, labels, map);
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
  plan(config) { return toStrategy(config, { labels: this.labels(), map: this.cardMap(), treasureNames: this.treasureNames() }); }
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
    if (config) { const p = this.plan(config); out.ready = !p.errors.length; out.errors = p.errors.slice(0, 8); out.warnings = p.warnings.slice(0, 5); }
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
