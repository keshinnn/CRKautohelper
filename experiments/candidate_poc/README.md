# A0–A2 isolated candidate research

Approved scope: finite offline candidate PoC readiness and proof research. This folder does not train on existing frozen annotations, replace a model, edit formal verifiers, or send game inputs. The installed V1 runtime is used read-only; no dependencies are installed into it.

Run from `C:/Users/User/Documents/Codex/CRK-Helper-V2` in PowerShell:

```powershell
& 'F:/CRK helper/.venv/Scripts/python.exe' -B -m unittest discover -s experiments/candidate_poc -p 'test_*.py' -v
& 'F:/CRK helper/.venv/Scripts/python.exe' -B experiments/candidate_poc/preflight.py --out artifacts/candidate-poc-new-run
node experiments/candidate_poc/proof_compatibility.cjs artifacts/candidate-poc-new-run/proof-compatibility.json
& 'F:/CRK helper/.venv/Scripts/python.exe' -B experiments/candidate_poc/run_research.py --out artifacts/candidate-poc-new-run
```

`preflight.py` makes a new immutable baseline ZIP (223 source/data/test files and 141 external dependency files), verifies every archived byte by SHA256, audits four previously exposed source videos, and locks positive/negative image hashes. An existing archive is never overwritten. To resume an interrupted inventory, use `--resume`; it checks the current baseline and existing archive before continuing.

`freeze_inputs.readiness()` is a **metadata admission check**, not an image/annotation certification service or permission to train. Review/provenance fields must be independently audited against original files and review records before any future training orchestrator may use them. The current admitted manifest contains zero records. It cannot enable training. No training entry point is installed or launched in this batch.

`proof_compatibility.cjs` uses existing same-frame observer output for schema probes, not a new detector. Removing template fields while retaining other old fields is a compatibility diagnostic, not proof that a neural proposal was validated. Proposal-only probes remove old absolute map authority. All probes are read-only.

`research_evidence.py` and `verify_research.cjs` demonstrate Python/Node agreement on PNG/RGB binding, an invertible source-to-letterbox transform, and fixed raw pixel-gradient samples. Node independently decodes supported 8-bit non-interlaced RGB PNGs and checks CRCs. Unsupported formats reject. The trusted source/context is supplied separately by the offline harness, not by the witness. This is a research assumption, not an implemented live trusted capture store.

**Reproducing samples is not proving a unique physical outer boundary.** The verifier always outputs false select/confirm/dispatch, outer-boundary, map-location, registration and identity flags. It neither emits formal authority nor recognizes a preview. Repeated frames cannot confirm a transaction because no transaction authority is produced at all. Offline PTS + 1ms in the real-PNG witness experiment is not a live freshness measurement.

Current results and limitations: [A0–A2 report](../../docs/reports/crk-helper-v2-candidate-poc-results.md).

## Continued A0: raw corpus and numerical annotation audit

2026-11-09: `artifacts/candidate-labeling-20261109-03/raw-corpus-v2.json` contains the240/80/80 raw pool across the four pre-reserved sources. The initial v1 extraction had front-loaded timeline sampling; its manifest/images/log remain preserved and excluded from the accepted raw-pool index. `sampling.py` now spans each entire source and preserves the original20 train QA indices. This is not a revision to any frozen G4 benchmark.

`annotation_audit.audit_full_frame(source, first, second)` reads and fully decodes the actual RGB PNG, then requires separate reviewer identities, exhaustive-review attestations and one-to-one class/visibility matches at IoU≥.90. It compares two NEW annotation drafts, not model output against ground truth. Its output always has `trainingAdmitted=false`: metadata attestations and agreement cannot by themselves certify physical truth or source/run/layout independence.

`duplicate_audit.audit_duplicates(records, protected)` validates asset hashes, dimensions and decoded RGB, detects exact repeated content despite PNG re-encoding, and queues whole-frame pHash similarities for review. No-match is not proof of perceptual/layout independence; low-information images are explicitly listed. The scripts do not remove difficult frames or read frozen truth to produce labels.

Current batch has four positive full-frame dual AI reviews (46 boxes) and three genuine empty-label hard-negative reviews. See [numerical label and400-frame report](../../docs/reports/crk-helper-v2-full-frame-labeling-2026-11-09.md). Remaining labels, complete layout/provenance audit and train/export environment readiness still gate training. No formal verifier or P5 input is enabled.

2026-11-12: isolated train/export entry is now `train_export.py`; official26n export/runtime smoke and68research tests pass. RealCRK fitting has NOT started:52/400 full-frame reviews,348 pending plus lineage qualification. See `docs/reports/crk-helper-v2-training-readiness-2026-11-12.md`. Use only a fully admitted manifest with bound review/provenance files; raw400 and current `training-admission-candidate.json` are rejected. Do not invoke `--worker` directly. One-use parent-supervised receipt, fixed50epoch/4wallhourCPU cap, no test pixels in fit dataset, no auto retry; no formal action authority.

Separate small research pilot (explicit user approval2026-11-12) now has ONE actual52-imageCRK training run and model artifacts. Read `artifacts/candidate-research-pilot-20261112-01/RESULTS.md`. FormalA1 remainsunconsumed; no modelreplacement/Verifierchange/P5. Do not automaticallytrainagain.
