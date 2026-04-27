# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27
**Active rounds:** 1 (bootstrap — no prior summary existed; written from master reality)

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable. This satisfies the Phase 1 walking-skeleton deliverables (#3, #4, #5, #6 per the Phase 1 plan).

Lexicon fixtures are the second major accomplishment. Seven fixture files are committed to `data/fixtures/`: four Accordance-sourced (`lex_halot.json` ~22 MB, `lex_bdag.json` ~38 MB, `lex_bdb_accordance.json` ~1 MB, `lex_km.json` ~25 MB) and three public-domain (`lex_bdb.json` ~38 MB, `lex_lsj.json` ~23 MB, `lex_thayer.json` ~5 MB). Iter-4 data quality fixes (PR #14) materially improved extraction: KM `gk_number` now 100% populated (was 0%); HALOT binyanim now 95.6% on verbs (was 0.1%); BDAG multi-sense parsing now working for 1,908 entries (was 0); BDB clean at 8,846 entries passing G.1. Genesis full corpus (1,532 verses, PR #8/11) is on master with HTML cleanup (PR #11).

The orchestration doc moved to v3 (PR #15), introducing the Topic Director / Synthesizer split. The research loop is now runnable in principle, but two gates block ML signal: (a) Plan #6 corpus assembly (per-token `token_id` + `fingerprint` + multi-dimensional metadata) does not yet exist — the model currently trains on raw Genesis parallel text with no lexicon augmentation; (b) known lexicon defects (Plan #7a/b/c) will degrade corpus quality if left unresolved before assembly. Model training has not been attempted at scale; there are no results in `results.tsv`; the chrF metric is a smoke scaffold only.

---

## What changed in the most recent round

The PR #11 → #13 → #14 → #15 chain merged in a single session (2026-04-27):

- **PR #11** (`e33a179`, `17df62c`): cleaned stray characters and HTML entities from `genesis_full_hebrew.json` (1,532 verses); updated `fetch_genesis_full.py` to prevent re-introduction.
- **PR #13** (`2e83853`, `f62d9e0`): iter-3 decoder redesign fixtures — all four Accordance lexicons pass G.1; BDAG body-residue corruption fixed.
- **PR #14** (`efc203a`): iter-4 critical fixes regenerating all four Accordance lexicons — KM gk_number 100%, HALOT binyanim 95.6%, BDAG multi-sense parsing live.
- **PR #15** (`dc6c4a5`, `1295624`): orchestration doc v3 — substance/orchestration split, Topic Director + Synthesizer roles, spawn templates, lessons appendix expanded.

These together mean: the extraction pipeline is now trustworthy enough to build on for Hebrew (HALOT + KM + BDB), the corpus fixture is clean, and the governance structure to run research iterations properly exists.

---

## Distance to product goal

**What we have:**
- Runnable end-to-end loop (prepare → train → score) on Genesis 1–3 fixture
- Full Genesis corpus (1,532 verses) clean on master
- Seven lexicon fixtures with known quality profile (iter-4)
- Phase 1 walking skeleton passing 3 smoke tests
- Gold corpus at `gold/catalog.json` (95 entries; 67 Genesis-heavy)
- Rubric at `gold/rubric.md` (15 patterns; 7 automatable)

**What's blocking:**
- Plan #6 not started: no per-token table with `token_id` + `fingerprint` + passage metadata exists; training currently runs on raw parallel text only, no lexicon-augmented features
- Plan #7b (BDB binyan coverage): 1.1% coverage — likely 50%+ of Hebrew verbs missing binyan extraction; this corrupts the core morphological signal for Hebrew verb semantics
- Plan #7c (HALOT multi-stem entries): `natan` / `shaphat` and other multi-stem lemmas missing from HALOT extraction
- Plan #7a (BDAG GK/Greek Mounce): 0% — not a Hebrew blocker but blocks Greek track
- No model has been trained at scale; no rubric metric result exists; chrF baseline unknown
- Rust export path (Phase 5) not designed

**What's next (Director's recommendation):**
Fix Plan #7b (BDB binyan) before Plan #6 assembly. A corpus built on 1.1% binyan coverage poisons morphological signal at the source. The fix is bounded (single defect class, known location). Plan #6 should not run until BDB binyan and HALOT multi-stem are resolved.

---

## Open questions

**For Director:**
- HALOT binyanim is at 95.6% on verbs. Is the remaining 4.4% acceptable for Plan #6, or does it need another pass before assembly?
- Plan #7b (BDB binyan 1.1%) vs Plan #7c (HALOT natan/shaphat): which defect has higher coverage impact per token? Need a count of affected tokens in the Genesis corpus before scheduling.

**For user:**
- Confirm Plan #6 corpus assembly schema: should `passage_id` be verse-level (e.g., `Gen.1.1`) or passage-level (pericopae blocks)? This determines how the passage_metadata table keys.
- Confirm whether `genesis_full` (all 1,532 verses) or just Genesis 1–3 fixture is the intended training corpus for the first model run.
- HALOT and BDB both have Hebrew-side coverage; KM is the Greek Mounce lexicon and also contains Hebrew cross-refs via `gk H{n}` pattern. Confirm: for Plan #6 Hebrew-track corpus, are KM's Hebrew cross-references in scope for token augmentation, or only HALOT/BDB?
