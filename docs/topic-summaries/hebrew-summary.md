# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 2 — post-Verifier-1)
**Active rounds:** 2

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable. This satisfies the Phase 1 walking-skeleton deliverables (#3, #4, #5, #6 per the Phase 1 plan).

Lexicon fixtures are the second major accomplishment. Seven fixture files are committed to `data/fixtures/`: four Accordance-sourced (`lex_halot.json` ~22 MB, `lex_bdag.json` ~38 MB, `lex_bdb_accordance.json` ~1 MB, `lex_km.json` ~25 MB) and three public-domain (`lex_bdb.json` ~38 MB, `lex_lsj.json` ~23 MB, `lex_thayer.json` ~5 MB). Iter-4 data quality fixes (PR #14) materially improved extraction: KM `gk_number` now 100% populated (was 0%); HALOT binyanim now 95.6% on verbs (was 0.1%); BDAG multi-sense parsing now working for 1,908 entries (was 0); BDB clean at 8,846 entries passing G.1. Genesis full corpus (1,532 verses, PR #8/11) is on master with HTML cleanup (PR #11).

The orchestration doc moved to v3 (PR #15), introducing the Topic Director / Synthesizer split. The research loop is now runnable in principle, but two gates block ML signal: (a) Plan #6 corpus assembly (per-token `token_id` + `fingerprint` + multi-dimensional metadata) does not yet exist — the model currently trains on raw Genesis parallel text with no lexicon augmentation; (b) known lexicon defects (Plan #7a/b/c) will degrade corpus quality if left unresolved before assembly. Model training has not been attempted at scale; there are no results in `results.tsv`; the chrF metric is a smoke scaffold only.

**Round 2 update (Verifier-1 findings):** BDB binyan coverage is **86.2%** (1,414 / 1,641 strict-verb entries), not the 1.1% stated in round 1. The round 1 director-note was based on a stale pending-pile claim; Verifier-1 measured the actual fixture. This is a significant positive finding — the BDB binyan defect is much smaller than believed. Three sub-defects remain: (1) 227 verb entries with `binyanim=None` (mechanical extraction gap); (2) הלך misclassified as `grammar_normalized=noun` across its 2 entries (POS normalizer failure); (3) עשה absent from fixture entirely (possible source omission or alternate-spelling filing). 0 over-extraction cases found. User chose Option A: close the 3 BDB sub-defects (Mode 3 Builder), then audit #7c HALOT, then Plan #6.

**Cross-repo update:** fellwork-api PR #6 merged to main at commit `47f7c7f`, shipping the decoder framework and Beta Code from font CMAP. This is the same framework that produced the iter-4 fixtures; future fix passes regenerating `lex_bdb.json` must use this decoder, not a different version. PRs #16 and #17 merged on autoresearch-win-rtx: `docs/domain-knowledge-cache.md` is now present (created via PR #16); v3 orchestration shipped via PR #17.

---

## What changed in the most recent round

**Round 1 (bootstrap, same session 2026-04-27):** The PR #11 → #13 → #14 → #15 chain merged:

- **PR #11** (`e33a179`, `17df62c`): cleaned stray characters and HTML entities from `genesis_full_hebrew.json` (1,532 verses); updated `fetch_genesis_full.py` to prevent re-introduction.
- **PR #13** (`2e83853`, `f62d9e0`): iter-3 decoder redesign fixtures — all four Accordance lexicons pass G.1; BDAG body-residue corruption fixed.
- **PR #14** (`efc203a`): iter-4 critical fixes regenerating all four Accordance lexicons — KM gk_number 100%, HALOT binyanim 95.6%, BDAG multi-sense parsing live.
- **PR #15** (`dc6c4a5`, `1295624`): orchestration doc v3 — substance/orchestration split, Topic Director + Synthesizer roles, spawn templates, lessons appendix expanded.
- **PR #16**: `docs/domain-knowledge-cache.md` created (BDB-specific patterns, HALOT patterns, Accordance binary formats, all domain hints consolidated).
- **PR #17**: v3 orchestration update.
- **fellwork-api PR #6** (`47f7c7f`): decoder framework + Beta Code from font CMAP shipped to main.

**Round 2 (post-Verifier-1, 2026-04-27):** Verifier-1 audited `verify/bdb-binyan` branch (commit `fcb0850`). The round 1 director-note claimed BDB binyan at 1.1% and treated it as a near-total absence. Verifier-1 found the actual coverage is **86.2%** — 1,414 of 1,641 strict-verb entries have binyanim populated using the real schema fields (`grammar_normalized` and `headword_consonantal`, not `pos` and `lemma`). The discrepancy came from the pending-pile claim never being measured against the current fixture. Verifier identified 3 residual sub-defects: 227 verb entries missing binyanim, הלך misclassified as noun, and עשה absent from fixture. Over-extraction is zero. User chose Option A: fix the 3 sub-defects (Mode 3 Builder on `fix/bdb-binyan-residuals`), then re-audit #7c HALOT, then Plan #6. Round 2 director-note contains the refined Builder brief.

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
- Plan #7b (BDB binyan residuals): 86.2% coverage on master — 3 small sub-defects remain (227 verb entries missing binyanim, הלך POS misclassification, עשה absent from fixture). These are bounded, not a structural absence. Builder dispatched on `fix/bdb-binyan-residuals`.
- Plan #7c (HALOT multi-stem entries): `natan` / `shaphat` reportedly missing — this claim has NOT been re-audited against current master. Per the round 1 lesson (stale 1.1% → actual 86.2%), the #7c baseline must be re-measured before any Builder runs on it. Director round 3 will trigger the #7c re-audit after Verifier-2 on BDB sub-defects passes.
- Plan #7a (BDAG GK/Greek Mounce): 0% — not a Hebrew blocker but blocks Greek track
- No model has been trained at scale; no rubric metric result exists; chrF baseline unknown
- Rust export path (Phase 5) not designed

**What's next (Director's recommendation):**
Builder on `fix/bdb-binyan-residuals` per round 2 director-note (investigation-first, then fix). After Verifier-2 passes: Director round 3 re-audits #7c HALOT baseline, then Plan #6. Plan #6 is closer than round 1 believed — BDB binyan was never the structural blocker it appeared to be.

---

## Open questions

**For Director (round 3, after Verifier-2):**
- Are #7c HALOT multi-stem and Plan #7a BDAG GK ALSO at higher coverage than the stale pending-pile claimed? The 1.1%→86.2% lesson must be applied: re-audit both against current master before any Builder runs. Expect similar surprises.
- HALOT binyanim is at 95.6% on verbs. Is the remaining 4.4% acceptable for Plan #6, or does it need another pass? Defer this question until #7b residuals close.

**For user (deferred — not blocking immediate work):**
- Confirm Plan #6 corpus assembly schema: should `passage_id` be verse-level (e.g., `Gen.1.1`) or passage-level (pericopae blocks)? This determines how the passage_metadata table keys.
- Confirm whether `genesis_full` (all 1,532 verses) or just Genesis 1–3 fixture is the intended training corpus for the first model run.
- HALOT and BDB both have Hebrew-side coverage; KM is the Greek Mounce lexicon and also contains Hebrew cross-refs via `gk H{n}` pattern. Confirm: for Plan #6 Hebrew-track corpus, are KM's Hebrew cross-references in scope for token augmentation, or only HALOT/BDB?

**Resolved (retired):**
- `docs/domain-knowledge-cache.md` existence question: NOW EXISTS (PR #16). BDB-specific patterns section present. Builder briefs should reference it directly.
