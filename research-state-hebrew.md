# Research state — Hebrew

**Last session:** 2026-04-26 (initial scaffold; no autoresearch session has yet run)
**Last commit:** `9e364dd` (master, post-PR #3)
**Branch:** none active yet — first session creates `autoresearch/<tag>` per `program.md`
**Phase:** Phase 1 (build) — research loop not yet runnable
**Current direction:** *Not started.* The autoresearch loop requires Phase 1 deliverables (`prepare_translate.py`, `evaluate_translate.py`, `train_translate.py`) to exist first.

## Direction status

- Misses on current direction: 0 / 3
- Best result this direction: n/a (no experiments run yet)

## Tried / kept / discarded (this branch)

| Commit | val_bpb | Status | Description |
|---|---|---|---|
| _(none yet)_ | | | |

## Open questions

- **Phase 1 simplification PR #5** is open. Once merged, the Phase 1 spec drops fellwork-api integration. The first Phase 1 build session should work against the simplified spec.
- **Tokenizer scheme.** Multilingual BPE with structural special tokens (`<phrase>`, `<clause>`, `<construct>`, suffix tags) per Phase 1 spec; vocab ~16k. Sanity-check on first session.
- **Model architecture.** Encoder-decoder vs prefix-LM. Phase 2 decision.
- **Rubric metric weights.** α=0.5 in spec; revisit after first eval pass.

## Next-session entry point

The autoresearch loop is not runnable yet. The next *productive* work for the Hebrew track is Phase 1 build, which is **linear engineering work, not autoresearch iteration**. Recommendation:

1. **Now:** Run a feature-dev session (separate from this orchestration) to build Phase 1 deliverables 3–6 (per the simplified spec in PR #5):
   - `prepare_translate.py` — pulls OSHB + Macula + reference English + lexicon entries
   - `evaluate_translate.py` — chrF + structural rubric metric returning a single scalar
   - `train_translate.py` — minimal seq2seq baseline runnable in 5 min on RTX 4070 12 GB
   - Phase 1 smoke test — end-to-end (prepare → train → eval) without crashes
2. **Then:** Once a working baseline exists with a runnable single-scalar metric, the per-direction autoresearch sessions begin.
3. **First autoresearch direction** (after Phase 1 is done): **Tier 1 — LR schedule sweep** per `program.md` (vary `WARMUP_RATIO`, `WARMDOWN_RATIO`, `FINAL_LR_FRAC`). Cheapest, most informative tier-1 area for a first run.

## Provenance

- Gold corpus: `gold/catalog.json` (95 entries; 67 Genesis, 10 Psalms, 15 NT, 3 Other-OT)
- Rubric: `gold/rubric.md` (15 patterns; 7 highly-automatable)
- Phase 1 design: `docs/superpowers/specs/2026-04-25-phase-1-design.md` (PR #5 revises)
- Lexicons in scope: HALOT, KM, BDB
- Source corpus: OSHB (Hebrew + ETCBC) + Macula Hebrew (phrase nodes)
