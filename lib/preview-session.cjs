'use strict';
const crypto = require('node:crypto');
const { validateProof, validateFrame } = require('./node-selector.cjs');
const { readDirectMapAnchor } = require('./observer-adapter.cjs');
const { verifyPreview } = require('./preview-verifier.cjs');
const { createGeometry, clientToScreen } = require('./geometry.cjs');
const active = new Set(['CLICK_PREPARED', 'CLICK_SENT', 'WAIT_PREVIEW', 'PREVIEW_STABLE']);

class PreviewSession {
 #clock; #dispatch; #trace; #state = 'IDLE'; #proof; #transactionId;
 #receiptAt; #mapSources=new Map();
 #sentAt; #first; #lastFrame; #settle; #action; #receipt;
 #seen = new Set(); #events = []; #observations = [];

 constructor({ clock, dispatch, trace = () => {} }) {
  if ([clock, dispatch, trace].some(f => typeof f !== 'function')) throw TypeError('explicit offline adapters required');
  this.#clock = clock; this.#dispatch = dispatch; this.#trace = trace;
 }

 #record(state, details = {}) {
  this.#state = state;
  const event = { atMs: this.#clock(), state, transactionId: this.#transactionId ?? null, ...details };
  this.#events.push(event);
  try { this.#trace(structuredClone(event)); }
  catch { this.#state = 'TRACE_FAILED'; this.#events.push({ atMs: this.#clock(), state: 'TRACE_FAILED' }); }
  if (!active.has(this.#state)) this.#settle?.();
  return this.#copy();
 }

 #copy() {
  return structuredClone({ state: this.#state, transactionId: this.#transactionId ?? null,
   mapAnchors:[...this.#mapSources.values()], receiptAtMs:this.#receiptAt??null, sentAtMs: this.#sentAt ?? null, deadlineMs: this.#sentAt == null ? null : this.#sentAt + 15000,
   proof: this.#proof ?? null, action: this.#action ?? null, receipt: this.#receipt ?? null,
   observations: this.#observations, events: this.#events });
 }

 // The replay driver must tick even when frames or receipts stop. Its injected
 // clock is also used for deadlines; no real timer is mixed with virtual time.
 tick() {
  if (active.has(this.#state) && this.#clock() - this.#sentAt >= 15000) {
   return this.#record(['CLICK_PREPARED','CLICK_SENT'].includes(this.#state) ? 'DISPATCH_UNCERTAIN' : 'PREVIEW_TIMEOUT');
  }
  return this.#copy();
 }
 snapshot() { return this.tick(); }

 async start(proof) {
  if (this.#state !== 'IDLE') return this.snapshot();
  try { validateProof(proof); validateFrame(proof.frame, this.#clock()); }
  catch (e) { return this.#record(e.code || 'SELECTION_PROOF_INVALID'); }
  this.#proof = proof; this.#lastFrame = proof.frame; this.#seen.add(proof.frame.id);
  this.#transactionId = crypto.randomUUID(); this.#sentAt = this.#clock();
  const f = proof.frame;
  const geometry = createGeometry({ frame: f, contentRect: [0, 0, f.width, f.height],
   analysisSize: [f.width, f.height], padding: [0, 0, 0, 0] });
  this.#action = Object.freeze({ kind: 'click', transactionId: this.#transactionId,
   frameId: f.id, geometryVersion: f.geometryVersion, clientPoint: Object.freeze([...proof.point]),
   screenPoint: Object.freeze(clientToScreen(proof.point, geometry)) });
  const cancelled = new Promise(resolve => { this.#settle = () => resolve({ cancelled: true }); });
  this.#record('CLICK_PREPARED', { action: this.#action, proof });
  if (this.#state === 'TRACE_FAILED') return this.snapshot();
  try { validateFrame(f, this.#clock()); }
  catch { return this.#record('FRAME_INVALID'); }
  this.tick();
  if (this.#state !== 'CLICK_PREPARED') return this.snapshot();
  this.#sentAt=this.#clock();this.#state='CLICK_SENT';
  // Invoke synchronously after reserving the transaction; attach both handlers
  // before yielding so thrown and rejected receipts are contained.
  let pending;
  try { pending = Promise.resolve(this.#dispatch(this.#action)).then(receipt => ({receipt}), error => ({error:String(error)})); }
  catch (error) { pending = Promise.resolve({error:String(error)}); }
  this.#record('CLICK_SENT',{atMs:this.#sentAt,action:this.#action});
  const outcome = await Promise.race([pending, cancelled]);
  this.tick();
  if (this.#state !== 'CLICK_SENT') return this.snapshot();
  if (outcome.error || outcome.cancelled) return this.#record('DISPATCH_UNCERTAIN', { error: outcome.error });
  this.#receipt = structuredClone(outcome.receipt ?? null);
  const r = this.#receipt;
  if (r?.transactionId !== this.#transactionId || r?.frameId !== f.id) return this.#record('DISPATCH_UNCERTAIN', { receipt:r });
  if (r.status === 'not_sent') return this.#record('DISPATCH_NOT_SENT', { receipt:r });
  if (r.status !== 'sent') return this.#record('DISPATCH_UNCERTAIN', { receipt:r });
  this.#receiptAt=this.#clock();
  return this.#record('WAIT_PREVIEW', { receipt:r });
 }

 observe(observation) {
  this.tick();
  if (!['WAIT_PREVIEW', 'PREVIEW_STABLE'].includes(this.#state)) return this.snapshot();
  const anchor=readDirectMapAnchor(observation);
  const o = structuredClone(observation), f = o?.frame;
  const entry = { observation:o, verdict:null };
  this.#observations.push(entry);
  const reject = code => { entry.verdict = {kind:'reject',code}; return this.#record(code,{frameId:f?.id,observation:o,verdict:entry.verdict}); };
  try { validateFrame(f,this.#clock()); } catch { return reject('FRAME_INVALID'); }
  const last = this.#lastFrame, video = this.#proof.sourceMode === 'video';
  if (f.windowKey !== this.#proof.frame.windowKey || this.#seen.has(f.id) ||
      f.atMs <= this.#sentAt || f.atMs <= last.atMs ||
      (video ? !Number.isFinite(f.sourcePtsMs) || f.sourcePtsMs <= last.sourcePtsMs : f.sourcePtsMs != null)) return reject('FRAME_INVALID');
  this.#seen.add(f.id); this.#lastFrame = f;
  for(const [id,source] of this.#mapSources)if(f.atMs-source.frame.atMs>2500)this.#mapSources.delete(id);
  // Verify private observation authority before copying it into the trace.
  // A serialized/copy-only observation cannot manufacture wait permission.
  const verdict = verifyPreview(this.#proof,observation,{mapSources:[...this.#mapSources.values()]}); entry.verdict = verdict;
  if (verdict.kind === 'reject') return this.#record(verdict.code,{frameId:f.id,observation:o,verdict});
  if(anchor&&anchor.zone===this.#proof.intent.zone&&f.atMs>this.#receiptAt){
   this.#mapSources.set(f.id,anchor);entry.mapAnchor=structuredClone(anchor);
  }
  if (verdict.kind === 'wait') { this.#first = null; return this.#record('WAIT_PREVIEW',{frameId:f.id,observation:o,verdict}); }
  if (!this.#first || f.geometryVersion !== this.#first.geometryVersion || f.width !== this.#first.width ||
      f.height !== this.#first.height || JSON.stringify(f.origin) !== JSON.stringify(this.#first.origin)) {
   this.#first = f; return this.#record('PREVIEW_STABLE',{frameId:f.id,observation:o,verdict});
  }
  return this.#record(f.atMs-this.#first.atMs < 200 ? 'PREVIEW_STABLE' : 'PREVIEW_CONFIRMED',{frameId:f.id,observation:o,verdict});
 }
}
module.exports = { PreviewSession };
