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
  pad.append(msg, where, hand, problems, controls, halt, recent);
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
    badge.textContent = label; badge.dataset.mode = m;
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

  // ---------- roster page: card mapping ----------
  const cardsBox = el('article', 'card section-space'); cardsBox.id = 'botCards';
  const ch = el('div', 'card-head'); ch.append(el('h2', '', '角色卡片對應'), el('span', 'tiny', '自動通關用來在隊伍設定裡認角色'));
  const cbody = el('div', 'pad'); const cintro = el('p', 'tiny', '每位出場角色要對應到一張遊戲內的角色卡片圖。名稱能唯一比對時會自動對應；比對不到或有多個可能時，請在這裡選擇。');
  const ctable = el('div', 'bot-cards'); const csave = button('儲存卡片對應', saveCards, 'btn primary'); csave.disabled = true;
  const cstate = el('p', 'tiny'); cstate.setAttribute('role', 'status');
  cbody.append(cintro, ctable, el('div', 'controls section-space'), cstate); cbody.querySelector('.controls').append(csave);
  cardsBox.append(ch, cbody); $('roster').append(cardsBox);
  let cardData = null;
  async function loadCards() {
    ctable.replaceChildren(el('p', 'tiny', '讀取中…'));
    try { cardData = await api('/api/bot/cards'); } catch (e) { ctable.replaceChildren(el('p', 'error', '讀取角色卡片失敗：' + e.message)); return; }
    ctable.replaceChildren();
    if (!cardData.roster.length) { ctable.append(el('p', 'tiny', '起始名單還沒有角色。先在上方選好起始 15 隻。')); return; }
    if (!cardData.labels.length) { ctable.append(el('p', 'error', '找不到角色卡片圖（bot/cards/labels.json）。')); return; }
    for (const r of cardData.roster) {
      const row = el('div', 'bot-card-row'), name = el('span', 'bot-card-name', r.name);
      const id = 'botCard-' + r.id, lab = el('label', 'sr-only', r.name + ' 的角色卡片'); lab.htmlFor = id;
      const sel = el('select'); sel.id = id; sel.dataset.id = r.id;
      sel.append(new Option('（未對應）', ''));
      for (const l of cardData.labels) sel.append(new Option(l, l, false, l === r.card));
      const img = el('img', 'bot-card-img'); img.alt = ''; img.width = 48; img.height = 48;
      const how = el('span', 'tiny', r.how === 'map' ? '已指定' : r.how === 'name' ? '依名稱自動對應' : '需要選擇');
      const show = () => { if (sel.value) { img.src = '/api/bot/card/' + encodeURIComponent(sel.value); img.hidden = false; } else img.hidden = true; };
      sel.onchange = () => { show(); how.textContent = '尚未儲存'; csave.disabled = false; cstate.textContent = '有未儲存的卡片對應'; };
      show(); row.append(img, name, lab, sel, how); ctable.append(row);
    }
  }
  async function saveCards() {
    const map = {}; for (const s of ctable.querySelectorAll('select')) map[s.dataset.id] = s.value;
    await api('/api/bot/cards', 'PUT', { map }); csave.disabled = true; cstate.textContent = '已儲存卡片對應'; toast('已儲存卡片對應'); loadCards(); poll();
  }
  document.querySelector('.nav').addEventListener('click', e => { if (e.target.closest('[data-page="roster"]')) loadCards(); });
  document.addEventListener('crk-config-refreshed', () => { if (activePage === 'roster') loadCards(); });
})();
