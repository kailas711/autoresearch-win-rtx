# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 3 — post-Verifier-2 PASS)
**Active rounds:** 3

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable. This satisfies the Phase 1 walking-skeleton deliverables (#3, #4, #5, #6 per the Phase 1 plan).

Lexicon fixtures are the second major accomplishment. Seven fixture files are committed to `data/fixtures/`: four Accordance-sourced (`lex_halot.json` ~22 MB, `lex_bdag.json` ~38 MB, `lex_bdb_accordance.json` ~1 MB, `lex_km.json` ~25 MB) and three public-domain (`lex_bdb.json` ~38 MB, `lex_lsj.json` ~23 MB, `lex_thayer.json` ~5 MB). Iter-4 data quality fixes (PR #14) materially improved extraction: KM `gk_number` now 100% populated (was 0%); HALOT binyanim now 95.6% on verbs (was 0.1%); BDAG multi-sense parsing now working for 1,908 entries (was 0); BDB clean at 8,846 entries passing G.1. Genesis full corpus (1,532 verses, PR #8/11) is on master with HTML cleanup (PR #11).

The orchestration doc moved to v3 (PR #15), introducing the Topic Director / Synthesizer split. The research loop is now runnable in principle, but two gates block ML signal: (a) Plan #6 corpus assembly (per-token `token_id` + `fingerprint` + multi-dimensional metadata) does not yet exist — the model currently trains on raw Genesis parallel text with no lexicon augmentation; (b) known lexicon defects (Plan #7a/b/c) will degrade corpus quality if left unresolved before assembly. Model training has not been attempted at scale; there are no results in `results.tsv`; the chrF metric is a smoke scaffold only.

**Round 2 update (Verifier-1 findings):** BDB binyan coverage is **86.2%** (1,414 / 1,641 strict-verb entries), not the 1.1% stated in round 1. The round 1 director-note was based on a stale pending-pile claim; Verifier-1 measured the actual fixture. Three sub-defects remained: (1) 227 verb entries with `binyanim=None`; (2) הלך misclassified as `grammar_normalized=noun`; (3) עשה absent from fixture. User chose Option A: close the 3 BDB sub-defects, then audit #7c HALOT, then Plan #6.

**Round 3 update (Verifier-2 PASS):** BDB binyan is now at **99.3%** (1,683 / 1,695 verb entries). All 3 named sub-defects are resolved. Builder investigation doc (`bdb-binyan-investigation.md`, commit `25d8b35`) traced all three to Tier 1 mechanical extractor bugs; Iron Law complied (investigation preceded fix by 7 minutes). The fix (commit `e52abd2` on `fix/bdb-binyan-residuals`) yielded a non-trivial bonus: 587 additional non-verb entries recovered by the compound-Strong's parser, expanding total fixture from 8,846 to 9,433 entries. Over-extraction remains 0; the recovered entries carry no binyanim. 5 Aramaic-stem entries were cross-verified against source body text by Verifier-2 — no hallucination. The 12 remaining `binyanim=None` entries are addendum/cross-ref stubs with no morphological data; these are accepted as known-source-gap, not a defect.

`docs/domain-knowledge-cache.md` now contains four BDB-specific subsections appended by the Builder: Aramaic stem labels (Pe./Pa./Haph./Ithpa./Shaph./Aph./Ithpe./Po.), Compound Strong's entries format, Implicit Qal verbs, and Roman-numeral headword prefix. These are project-bound for all future BDB Builder dispatches.

**Cross-repo status:** fellwork-api PR #6 merged to main at `47f7c7f` (decoder framework). fellwork-api PR #8 (BDB residual fix) opened and paired with autoresearch `fix/bdb-binyan-residuals` branch. PR #6 (fellwork-api decoder framework) is the decoder dependency for any future `lex_bdb.json` regeneration.

---

## What changed in the most recent round

**Round 2 (post-Verifier-1, 2026-04-27):** Verifier-1 audited `verify/bdb-binyan` branch (commit `fcb0850`), measured real BDB coverage at 86.2% (1,414/1,641 verb entries), correcting the stale 1.1% pending-pile claim. Round 2 director-note dispatched a Mode 3 Builder on `fix/bdb-binyan-residuals` with investigation-first discipline. Round 3 routes the Verifier-2 result and plans the #7c re-audit.

**Round 3 (post-Verifier-2, 2026-04-27 — this round):** Three phases closed cleanly.

Builder dispatched on `fix/bdb-binyan-residuals` produced `docs/audits/bdb-binyan-investigation.md` (commit `25d8b35`) tracing all 3 sub-defects to Tier 1 mechanical extractor bugs: (1) Aramaic stem labels absent from `BDB_BINYANIM` list in `bdb_hooks.rs`; (2) compound-Strong's `N, M\t` format dropped by `strongs_tab` parser (root cause of both הלך absence and the 227-verb residual overlap); (3) Roman-numeral headword prefix `I.`/`II.` causing empty consonantal decode for עשה. Fix commit `e52abd2` applied all three: expanded Aramaic stem table, compound-Strong's parser, and Roman-numeral headword fallback. Fixture regenerated from fellwork-api decoder at `47f7c7f`. fellwork-api PR #8 opened in parallel.

Verifier-2 audited `verify/bdb-binyan-r2` branch (commit `3e771d2`) and issued **PASS**: verb coverage 1,683/1,695 (99.3%), all named samples pass independently, over-extraction 0, Iron Law complied, 5 Aramaic-stem entries cross-verified against source body text with no hallucination detected. Compound-Strong's bonus (+587 entries) verified structurally clean — no binyanim added to non-verb entries. The 810-entry total expansion (54 verb + 587 non-verb + absorption cleanup) is consistent with baseline patterns.

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
- Plan #7b (BDB binyan): **RESOLVED.** 99.3% on `fix/bdb-binyan-residuals`; fellwork-api PR #8 open. Pending merge coordination (see Open questions).
- Plan #7c (HALOT multi-stem): `natan` / `shaphat` reportedly missing — baseline claim NOT yet re-audited. Per the round 1 lesson, re-measure before any Builder runs. Director round 3 dispatches Verifier-only on `verify/halot-multistem`. Outcome determines whether #7c needs a Builder fix or is another stale baseline.
- Plan #7a (BDAG GK/Greek Mounce): 0% — not a Hebrew blocker; deferred to Greek track
- No model trained at scale; no rubric metric result; chrF baseline unknown
- Rust export path (Phase 5) not designed

**What's next (Director's recommendation):**
Verifier-only audit on `verify/halot-multistem` per round 3 director-note brief. This is the last data-quality gate before Plan #6. If #7c re-audit reveals stale baseline (similar to #7b), Plan #6 corpus assembly is immediately next. If real defects found, Director round 4 refines a Builder brief. BDB binyan ML-acceptable at 99.3%; remaining 12 null entries are known-source-gap stubs and do not block corpus assembly.

---

## Open questions

**Immediate (round 3 in-flight):**
- #7c HALOT multi-stem baseline: does the current `lex_halot.json` on master actually reflect "natan/shaphat missing"? The round 1 lesson mandates re-measurement. Verifier-only dispatch on `verify/halot-multistem` is the immediate next action. If HALOT multi-stem coverage is ≥80% and named samples pass, the #7c claim is stale and Plan #6 is unblocked.
- HALOT binyanim is at 95.6% on verbs. Is the remaining 4.4% an acceptable known-gap for Plan #6, or does it require a Builder pass? Defer this question until the #7c Verifier finding is known — if #7c reveals stale baseline, the 4.4% is the only open HALOT question.

**Cross-repo PR coordination (orchestration, not data quality):**
- fellwork-api PR #8 (BDB extractor fix, branch `fix/bdb-binyan-residuals`) must merge to fellwork-api master BEFORE the autoresearch PR is opened. The autoresearch `fix/bdb-binyan-residuals` branch regenerated `lex_bdb.json` against a fellwork-api branch HEAD (`171fb0a`) that has not yet merged to fellwork-api main. If the autoresearch PR is merged first, the fixture in autoresearch master was generated from a non-main decoder revision. Correct merge order: (1) merge fellwork-api PR #8, (2) open autoresearch PR from `fix/bdb-binyan-residuals`, (3) merge autoresearch PR. Flag for Team Lead.
- HALOT `domain-knowledge-cache.md` note (round 1 pattern): if #7c Verifier finds the baseline stale, no new domain knowledge is needed for that lexicon. If real defects found, the Builder brief for #7c must reference the HALOT-specific patterns section of `docs/domain-knowledge-cache.md`.

**For user (deferred — not blocking immediate work):**
- Confirm Plan #6 corpus assembly schema: should `passage_id` be verse-level (e.g., `Gen.1.1`) or passage-level (pericopae blocks)? This determines how the passage_metadata table keys.
- Confirm whether `genesis_full` (all 1,532 verses) or just Genesis 1–3 fixture is the intended training corpus for the first model run.
- HALOT and BDB both have Hebrew-side coverage; KM is the Greek Mounce lexicon and also contains Hebrew cross-refs via `gk H{n}` pattern. Confirm: for Plan #6 Hebrew-track corpus, are KM's Hebrew cross-references in scope for token augmentation, or only HALOT/BDB?

**Resolved (retired):**
- `docs/domain-knowledge-cache.md` existence question: NOW EXISTS (PR #16). BDB-specific patterns section present and updated with 4 new subsections from the round 3 Builder investigation. Builder briefs should reference it directly.
- BDB binyan structural blocker: RESOLVED. 99.3% is ML-acceptable; Plan #6 is no longer blocked on BDB binyan.
