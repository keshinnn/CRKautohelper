'use strict';
// 自動通關（MuMu runner）— overview card, game preview, manual hand-over, card mapping on the roster page.
// Talks to /api/bot/*; the runner itself (bot/runner.py) owns all game input.
(() => {
  const MODE = {
    idle: ['待命', '尚未開始自動通關'], auto: ['自動執行中', ''], manual: ['等待玩家手動', ''],
    paused: ['已暫停', ''], stopped: ['已停止', ''], error: ['發生錯誤', ''], loading: ['讀取中', '正在讀取自動通關狀態…'],
  };
  let st = null, pending = false, lastFrameN = -1, failed = 0;

  // ---------- overview card ----------
  const card = el('article', 'card section-space bot-card'); card.id = 'botRunner';
  const head = el('div', 'card-head'), title = el('h2', '', '自動通關'), badge = el('span', 'badge bot-badge', '讀取中');
  head.append(title, badge);
  const pad = el('div', 'pad');
  const msg = el('p', 'bot-message'); msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite');
  const where = el('p', 'tiny bot-where');
  // hand-over banner (manual node)
  const hand = el('div', 'bot-handover'); hand.hidden = true; hand.setAttribute('role', 'region'); hand.setAttribute('aria-label', '手動關卡');
  const handTitle = el('h3', '', ''), handNote = el('p', 'tiny', ''), handHelp = el('p', 'tiny',
    '程式在這段期間不會點擊遊戲。你打到這一層的勝利畫面時，程式會自動接手；如果你已經自己離開勝利畫面，請按下面的按鈕。');
  const handBtn = button('我已完成這關，交還程式', () => command('resume'), 'btn primary');
  hand.append(handTitle, handNote, handHelp, handBtn);
  // problems that block starting
  const problems = el('div', 'bot-problems'); problems.hidden = true;
  const controls = el('div', 'controls section-space');
  const startBtn = button('開始自動通關', () => command('start', { reset: false }), 'btn primary');
  const resetBtn = button('從第一層重新開始', () => command('start', { reset: true }), 'btn');
  resetBtn.title = '清除本機的進度紀錄後開始；遊戲內進度不受影響，程式會依地圖標頭重新定位。';
  const stopBtn = button('停止', () => command('stop'), 'btn danger');
  controls.append(startBtn, resetBtn, stopBtn);
  const halt = el('div', 'notice bot-halt'); halt.hidden = true;
  const haltText = el('p', '', ''), haltBtn = button('清除失敗鎖定', () => command('clear-halt'), 'btn');
  halt.append(haltText, el('p', 'tiny', '同一層失敗超過重試次數時程式會鎖定。請先調整隊伍或配置，清除後再開始。'), haltBtn);
  const recent = el('details', 'bot-recent section-space'); const sum = el('summary', '', '最近動作'); const list = el('ol', 'bot-log');
  recent.append(sum, list);
  // layout: state + route on the left, actions on the right; hand-over plate spans the card when it is your turn
  const stateBig = el('div', 'bot-state-label', '讀取中');
  const route = el('ol', 'bot-route'); route.setAttribute('aria-label', '本區路線');
  const routeHead = el('p', 'tiny bot-route-head', '');
  const left = el('div', 'bot-left'); left.append(stateBig, msg, where, routeHead, route);
  const right = el('div', 'bot-right'); const ctrlHelp = el('p', 'tiny bot-ctrl-help', '程式會依攻略逐層前進；未確認的畫面或角色會停下等你。');
  controls.classList.add('bot-controls'); right.append(controls, ctrlHelp);
  const body = el('div', 'bot-body'); body.append(left, right);
  pad.append(hand, body, problems, halt, recent);
  card.append(head, pad);
  const overview = $('overview');
  overview.insertBefore(card, overview.querySelector('.grid'));
  // the old simulation card would be a second, fake "start" — hide it
  const simCard = $('run')?.closest('article'); if (simCard) simCard.hidden = true;
  // the stat tiles above described the simulation; they now show the real runner
  const relabel = (id, label, sub) => { const box = $(id)?.closest('.stat'); if (!box) return; const l = box.querySelector('.label'), s = box.querySelector('.sub'); if (l && label) l.textContent = label; if (s && sub !== undefined) s.textContent = sub; };
  relabel('status', '執行狀態', '自動通關（MuMu）'); relabel('progress', '目前進度', undefined);

  function setBusy(b) { pending = b; for (const x of [startBtn, resetBtn, stopBtn, handBtn, haltBtn]) x.disabled = b || x.disabled; }

  function render(s) {
    st = s; const m = s ? s.mode : 'loading';
    const [label, idleText] = MODE[m] || [m, ''];
    badge.textContent = label; badge.dataset.mode = m; card.dataset.mode = m; stateBig.textContent = label;
    renderRoute(s && s.route);
    msg.textContent = s ? (s.message || idleText) : MODE.loading[1];
    where.textContent = s && s.zone ? `進度紀錄：區域 ${s.zone}・下一層 第 ${(s.step ?? 0) + 1} 層` + (s.age != null && s.running ? `・${s.age} 秒前更新` : '') : '';
    const running = !!(s && s.running);
    // manual hand-over
    hand.hidden = !(s && s.mode === 'manual');
    if (s && s.manual) { handTitle.textContent = `請接手：區域 ${s.manual.zone}・第 ${s.manual.floor} 層`; handNote.textContent = s.manual.note || ''; }
    // blocking problems (only when not running)
    problems.replaceChildren(); problems.hidden = true;
    if (s && !running && s.errors && s.errors.length) {
      problems.hidden = false;
      problems.append(el('p', 'error', '攻略還不能自動執行：'));
      const ul = el('ul', 'tiny'); for (const e of s.errors) ul.append(el('li', '', e)); problems.append(ul);
      const fix = el('div', 'controls');
      fix.append(button('前往攻略配置', () => selectPage('strategy'), 'btn'), button('設定角色卡片', () => { selectPage('roster'); $('botCards')?.scrollIntoView(); }, 'btn'));
      problems.append(fix);
    }
    if (s && !running && s.warnings && s.warnings.length) problems.append(...s.warnings.map(w => el('p', 'tiny', '提醒：' + w))), problems.hidden = false;
    // buttons
    const ready = !!(s && s.ready);
    startBtn.textContent = s && s.zone ? '繼續自動通關' : '開始自動通關';
    startBtn.disabled = pending || !s || running || !ready;
    resetBtn.disabled = pending || !s || running || !ready;
    stopBtn.disabled = pending || !running;
    halt.hidden = !(s && s.halt); haltText.textContent = s && s.halt ? '已鎖定：' + s.halt : '';
    haltBtn.disabled = pending || running;
    handBtn.disabled = pending;
    // overview stats + preview
    $('status').textContent = label;
    if (s && s.zone) { $('progress').textContent = '區域 ' + s.zone; $('floor').textContent = '第 ' + ((s.step ?? 0) + 1) + ' 層'; }
    if (s && s.frame && s.n !== lastFrameN) {
      lastFrameN = s.n; const img = $('gamePreviewImage');
      img.src = '/api/bot/frame?n=' + s.n; img.alt = '自動通關最近一次看到的遊戲畫面';
      $('gamePreviewStatus').textContent = '自動通關畫面・第 ' + s.n + ' 步';
    }
  }

  const TYPE = { battle: '戰鬥', random: '節點', heal: '恢復', boss: '王關' };
  function renderRoute(r) {
    route.replaceChildren(); routeHead.textContent = '';
    if (!r || !r.floors.length) return;
    routeHead.textContent = '區域 ' + r.zone + ' 路線';
    for (const f of r.floors) {
      const li = el('li', 'bot-floor is-' + f.state + (f.manual ? ' is-manual' : '') + (f.type === 'boss' ? ' is-boss' : ''));
      li.append(el('span', 'bot-floor-n', f.type === 'boss' ? '王' : String(f.floor)), el('span', 'bot-floor-t', f.manual ? '手動' : TYPE[f.type] || f.type));
      li.title = (f.type === 'boss' ? '王關' : '第 ' + f.floor + ' 層') + '：' + (TYPE[f.type] || f.type) + (f.manual ? '（玩家手動）' : '') + ({ done: '・已完成', current: '・目前', next: '' })[f.state];
      if (f.state === 'current') li.setAttribute('aria-current', 'step');
      route.append(li);
    }
  }
  function renderLog(rows) {
    list.replaceChildren();
    for (const r of rows.slice(-15).reverse()) {
      const li = el('li', 'bot-log-' + r.kind); li.textContent = (r.n ? '#' + r.n + ' ' : '') + r.text; list.append(li);
    }
    sum.textContent = rows.length ? '最近動作（' + rows.length + '）' : '最近動作（尚無紀錄）';
  }

  async function poll() {
    if (pending || !authState?.authenticated || document.hidden) return;
    if (activePage !== 'overview' && st && !st.running) return;   // keep watching while it runs (hand-over toast)
    try {
      const prev = st && st.mode, s = await api('/api/bot/status'); failed = 0; render(s);
      if (s.mode === 'manual' && prev !== 'manual') toast('手動關卡：請到遊戲中接手（區域 ' + s.manual?.zone + '・第 ' + s.manual?.floor + ' 層）');
      if (activePage === 'overview' && recent.open) renderLog(await api('/api/bot/log'));
    } catch (e) {
      if (++failed >= 3) { badge.textContent = '連線中斷'; badge.dataset.mode = 'error'; msg.textContent = '無法讀取自動通關狀態：' + e.message; }
    }
  }

  async function command(name, data = {}) {
    if (pending) return; setBusy(true);
    try {
      if (name === 'start' && typeof dirty !== 'undefined' && dirty) await persist(true);   // run what the user sees
      await api('/api/bot/' + name, 'POST', data);
      toast({ start: data.reset ? '已從第一層重新開始' : '自動通關已開始', stop: '已送出停止，目前動作完成後停下', resume: '已交還程式，繼續自動通關', 'clear-halt': '已清除失敗鎖定' }[name]);
    } catch (e) { toast(e.message); msg.textContent = e.message; }
    finally { pending = false; setTimeout(poll, 600); }
  }

  recent.addEventListener('toggle', () => { if (recent.open) guard(async () => renderLog(await api('/api/bot/log')))(); });
  document.querySelector('.nav').addEventListener('click', () => setTimeout(poll, 0));
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  render(null); setInterval(poll, 2000); setTimeout(poll, 300);

  // ---------- roster page: confirmed in-game cards + inbox of unknown cards ----------
  const cardsBox = el('article', 'card section-space'); cardsBox.id = 'botCards';
  const ch = el('div', 'card-head'); ch.append(el('h2', '', '遊戲內角色卡片'), el('span', 'tiny', '自動通關選角只認這裡確認過的卡片'));
  const cbody = el('div', 'pad');
  cbody.append(el('p', 'tiny', '自動通關在「隊伍設定」只會點選已確認的遊戲內卡片；不在這裡的角色，程式會停下來等你確認，不會用猜的。'));
  const ctable = el('div', 'bot-cards'); const cstate = el('p', 'tiny'); cstate.setAttribute('role', 'status');
  const csave = button('儲存舊版名稱對應', saveCards, 'btn'); csave.disabled = true; csave.hidden = true;
  const ihead = el('div', 'bot-inbox-head'); const ititle = el('h3', '', '待確認的新卡片');
  const isuggest = button('產生辨識建議', suggest, 'btn'); ihead.append(ititle, isuggest);
  const ihelp = el('p', 'tiny', '程式在隊伍設定畫面看到卡片庫沒有的卡片時會存到這裡。角色模型會給出判定（沒把握時不判定）；確認後加入卡片庫。');
  const inbox = el('div', 'bot-inbox');
  const cctrl = el('div', 'controls section-space'); cctrl.append(csave);
  cbody.append(ctable, cctrl, cstate, ihead, ihelp, inbox);
  cardsBox.append(ch, cbody); $('roster').append(cardsBox);
  let cardData = null;
  const charName = id => (C?.characters.find(c => c.id === id)?.name) || id;
  function characterSelect(id, first) {
    const sel = el('select'); sel.id = id; sel.append(new Option('選擇角色…', ''));
    const used = new Set();
    const group = (label, items) => { if (!items.length) return; const g = document.createElement('optgroup'); g.label = label; for (const [v, t] of items) { if (used.has(v)) continue; used.add(v); g.append(new Option(t, v)); } if (g.children.length) sel.append(g); };
    group('模型判定與相似角色', first);
    const roster = [...(C?.initialRoster || []), ...(C?.extraRoster || [])];
    group('起始名單', roster.map(r => [r, charName(r)]));
    group('全部角色', (C?.characters || []).map(c => [c.id, c.name]));
    return sel;
  }
  async function loadCards() {
    ctable.replaceChildren(el('p', 'tiny', '讀取中…')); inbox.replaceChildren();
    try { cardData = await api('/api/bot/cards'); } catch (e) { ctable.replaceChildren(el('p', 'error', '讀取角色卡片失敗：' + e.message)); return; }
    ctable.replaceChildren(); csave.hidden = true;
    if (!cardData.roster.length) ctable.append(el('p', 'tiny', '起始名單還沒有角色。先在上方選好起始 15 隻。'));
    for (const r of cardData.roster) {
      const row = el('div', 'bot-card-row'), name = el('span', 'bot-card-name', r.name);
      const img = el('img', 'bot-card-img'); img.alt = ''; img.width = 48; img.height = 48;
      if (r.inBank) {
        img.src = '/api/bot/bank-image/' + encodeURIComponent(r.id);
        row.append(img, name, el('span', 'bot-card-ok', '已確認'), el('span'));
      } else {
        // legacy short-name templates (bot/cards/labels.json) can still stand in until a confirmed card exists
        const id = 'botCard-' + r.id, lab = el('label', 'sr-only', r.name + ' 的舊版卡片名稱'); lab.htmlFor = id;
        const sel = el('select'); sel.id = id; sel.dataset.id = r.id; sel.append(new Option('（沒有遊戲內卡片）', ''));
        for (const l of cardData.labels) sel.append(new Option('舊版：' + l, l, false, l === r.card));
        sel.onchange = () => { csave.disabled = false; csave.hidden = false; cstate.textContent = '有未儲存的對應'; };
        img.hidden = true; const st = el('span', 'bot-card-missing', r.card ? '使用舊版名稱對應' : '需要遊戲內卡片');
        row.append(img, name, lab, sel); row.append(st);
      }
      ctable.append(row);
    }
    const items = cardData.inbox || [];
    ititle.textContent = '待確認的新卡片' + (items.length ? `（${items.length}）` : '');
    isuggest.disabled = !items.some(i => !i.suggestions);
    if (!items.length) { inbox.append(el('p', 'tiny muted', '目前沒有待確認的卡片。')); return; }
    for (const it of items) {
      const box = el('div', 'bot-inbox-item'), img = el('img', 'bot-inbox-img'); img.src = '/api/bot/inbox-image/' + it.file; img.alt = '遊戲中看到、尚未確認的角色卡片';
      const sid = 'botInbox-' + it.file.slice(0, 16), lab = el('label', 'tiny', '這是哪位角色？'); lab.htmlFor = sid;
      const sugg = (it.suggestions || []).slice(0, 3).map(s => [s.id, (s.id === it.modelId ? '模型判定：' : '') + `${s.name}（相似度 ${s.similarity.toFixed(2)}）`]);
      const sel = characterSelect(sid, sugg);
      const verdict = it.modelId ? `模型判定為「${charName(it.modelId)}」並通過檢查；請核對後確認。` : it.suggestions ? '模型無法確定是誰' + (it.modelReason ? `（${it.modelReason.replace('low score', '相似度不足').replace('ambiguous', '與其他角色太接近').replace('no geometric support', '細節對不上')}）` : '') + '，請自行選擇。' : '尚無模型判定';
      const ok = button('確認', async () => {
        if (!sel.value) throw new Error('請先選擇角色');
        await api('/api/bot/inbox/confirm', 'POST', { file: it.file, characterId: sel.value });
        toast('已加入確認卡片：' + charName(sel.value)); loadCards(); poll();
      }, 'btn primary');
      const no = button('不是角色卡片', async () => { await api('/api/bot/inbox/dismiss', 'POST', { file: it.file }); loadCards(); }, 'btn');
      const acts = el('div', 'controls'); acts.append(ok, no);
      box.append(img, lab, sel, el('p', 'tiny' + (it.modelId ? '' : ' muted'), verdict), acts); inbox.append(box);
    }
  }
  async function suggest() {
    await api('/api/bot/inbox/suggest', 'POST', {}); cstate.textContent = '正在產生建議（約半分鐘）…';
    setTimeout(async () => { await loadCards(); cstate.textContent = ''; }, 30000);
  }
  async function saveCards() {
    const map = {}; for (const s of ctable.querySelectorAll('select[data-id]')) map[s.dataset.id] = s.value;
    await api('/api/bot/cards', 'PUT', { map }); csave.disabled = true; cstate.textContent = '已儲存'; toast('已儲存舊版名稱對應'); loadCards(); poll();
  }
  document.querySelector('.nav').addEventListener('click', e => { if (e.target.closest('[data-page="roster"]')) loadCards(); });
  document.addEventListener('crk-config-refreshed', () => { if (activePage === 'roster') loadCards(); });
})();
