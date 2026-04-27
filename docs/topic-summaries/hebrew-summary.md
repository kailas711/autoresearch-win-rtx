# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 4 — post-Verifier-3 NEEDS_FIX; Option A investigation-first)
**Active rounds:** 4

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable. This satisfies the Phase 1 walking-skeleton deliverables (#3, #4, #5, #6 per the Phase 1 plan).

Lexicon fixtures are the second major accomplishment. Seven fixture files are committed to `data/fixtures/`: four Accordance-sourced (`lex_halot.json` ~22 MB, `lex_bdag.json` ~38 MB, `lex_bdb_accordance.json` ~1 MB, `lex_km.json` ~25 MB) and three public-domain (`lex_bdb.json` ~38 MB, `lex_lsj.json` ~23 MB, `lex_thayer.json` ~5 MB). Iter-4 data quality fixes (PR #14) materially improved extraction: KM `gk_number` now 100% populated (was 0%); HALOT binyanim now 95.6% on verbs (was 0.1%); BDAG multi-sense parsing now working for 1,908 entries (was 0); BDB clean at 8,846 entries passing G.1. Genesis full corpus (1,532 verses, PR #8/11) is on master with HTML cleanup (PR #11).

The orchestration doc moved to v3 (PR #15), introducing the Topic Director / Synthesizer split. The research loop is now runnable in principle, but two gates block ML signal: (a) Plan #6 corpus assembly (per-token `token_id` + `fingerprint` + multi-dimensional metadata) does not yet exist — the model currently trains on raw Genesis parallel text with no lexicon augmentation; (b) known lexicon defects (Plan #7a/b/c) will degrade corpus quality if left unresolved before assembly. Model training has not been attempted at scale; there are no results in `results.tsv`; the chrF metric is a smoke scaffold only.

**Round 2 update (Verifier-1 findings):** BDB binyan coverage is **86.2%** (1,414 / 1,641 strict-verb entries), not the 1.1% stated in round 1. The round 1 director-note was based on a stale pending-pile claim; Verifier-1 measured the actual fixture. Three sub-defects remained: (1) 227 verb entries with `binyanim=None`; (2) הלך misclassified as `grammar_normalized=noun`; (3) עשה absent from fixture. User chose Option A: close the 3 BDB sub-defects, then audit #7c HALOT, then Plan #6.

**Round 3 update (Verifier-2 PASS):** BDB binyan is now at **99.3%** (1,683 / 1,695 verb entries). All 3 named sub-defects are resolved. Builder investigation doc (`bdb-binyan-investigation.md`, commit `25d8b35`) traced all three to Tier 1 mechanical extractor bugs; Iron Law complied (investigation preceded fix by 7 minutes). The fix (commit `e52abd2` on `fix/bdb-binyan-residuals`) yielded a non-trivial bonus: 587 additional non-verb entries recovered by the compound-Strong's parser, expanding total fixture from 8,846 to 9,433 entries. Over-extraction remains 0; the recovered entries carry no binyanim. 5 Aramaic-stem entries were cross-verified against source body text by Verifier-2 — no hallucination. The 12 remaining `binyanim=None` entries are addendum/cross-ref stubs with no morphological data; these are accepted as known-source-gap, not a defect.

`docs/domain-knowledge-cache.md` now contains four BDB-specific subsections appended by the Builder: Aramaic stem labels (Pe./Pa./Haph./Ithpa./Shaph./Aph./Ithpe./Po.), Compound Strong's entries format, Implicit Qal verbs, and Roman-numeral headword prefix. These are project-bound for all future BDB Builder dispatches.

**Cross-repo BDB status (closed):** fellwork-api PR #6 merged to main at `47f7c7f` (decoder framework). fellwork-api PR #8 (BDB residual fix) **merged** to fellwork-api main at commit `43612c3`. autoresearch PR #13 opened (BDB cross-repo close-out — fixture committed against the now-merged fellwork-api decoder). The BDB binyan path is closed end-to-end; BDB does not block Plan #6.

**Round 4 update (Verifier-3 NEEDS_FIX — structural HALOT defect):** Verifier-3 audited `verify/halot-multistem` (commit `49f3d9e`) and issued NEEDS_FIX. The defect is larger and more structural than the pending-pile claim implied. Full counts: 6,632 total entries (near 6,672 target — entry count is fine); `grammar_normalized` distribution: **None=3,120 (47%), noun=2,953, verb=298, adjective=167, adverb=54, preposition=20, interj.=15, conjunction=5**. Only 298 entries are classified as verbs — far below the ~1,500+ expected for a full Hebrew lexicon of this scope. 10+ high-frequency named verbs (נתן, שפט, אמר, עשה, בוא, ראה, ידע, שאל, שוב, דבר) are absent from the verb pool; two (ראה, עשה) are absent from the fixture entirely. The binyan extractor itself is sound (PASS on sample quality, 0 over-extraction) — the defect is upstream: the grammar classifier does not fire for ~3,120 entries, so the binyan extractor never receives them. Verifier-3's hypothesis: a parser state issue when walking the HALOT `.atool` binary drops POS section headers for these entries. `docs/domain-knowledge-cache.md` HALOT section documents binyan markers and cross-ref patterns; structural HALOT binary format info (Aramaic/Hebrew section boundary, binary format version markers) is not yet cached — flagged as Builder open question. Plan #6 is blocked on HALOT until grammar classifier defect is resolved. User chose **Option A (investigation-first)**: dispatch an Investigation Builder to diagnose root cause before any fix code.

---

## What changed in the most recent round

**Round 3 (post-Verifier-2, 2026-04-27):** BDB binyan residuals closed cleanly at 99.3%. Verifier-2 PASS. Builder investigation traced all 3 sub-defects to Tier 1 mechanical extractor bugs. Fix applied, fixture regenerated, fellwork-api PR #8 opened. Round 3 routed the PASS finding and dispatched Verifier-3 on `verify/halot-multistem` to re-baseline the #7c HALOT claim before any Builder fix work.

**fellwork-api PR #8 merged (43612c3); autoresearch PR #13 opened (2026-04-27):** The BDB cross-repo fix is now on fellwork-api main. autoresearch PR #13 opens the autoresearch-side close-out (fixture generated from a merged decoder). BDB binyan path is fully closed: no further action required on #7b.

**Round 4 (post-Verifier-3, 2026-04-27 — this round):** Verifier-3 issued NEEDS_FIX on `verify/halot-multistem`. The defect is structural: 47% of the 6,632 HALOT entries have `grammar_normalized=None`, and only 298 entries appear as verbs — a fraction of the ~1,500+ expected. Named verbs (נתן, שפט, אמר, עשה, בוא, ראה, ידע, שאל, שוב, דבר) are absent from the verb pool. The binyan extractor is not defective (PASS on quality and over-extraction); it is simply not being fed the correct input entries because grammar classification fails upstream. Verifier-3's structural hypothesis points to the `extract_grammar` → `pattern_list` pipeline in fellwork-api's `pipeline.rs` failing to find the grammar label for ~3,120 entries — possibly due to the 200-char body scan limit documented in `halot_hooks.rs`, or a body-split issue that places the grammar token outside the scanned window.

User chose **Option A**: Investigation-only Builder dispatch on `fix/halot-grammar-investigation`. No fix code this round. Investigation deliverable is `docs/audits/halot-grammar-investigation.md`. Director rounds 5+ will scope the fix after investigation findings.

---

## Distance to product goal

**What we have:**
- Runnable end-to-end loop (prepare → train → score) on Genesis 1–3 fixture
- Full Genesis corpus (1,532 verses) clean on master
- Seven lexicon fixtures with known quality profile (iter-4)
- Phase 1 walking skeleton passing 3 smoke tests
- Gold corpus at `gold/catalog.json` (95 entries; 67 Genesis-heavy)
- Rubric at `gold/rubric.md` (15 patterns; 7 automatable)
- BDB binyan: **DONE** — 99.3%; fellwork-api PR #8 merged at `43612c3`; autoresearch PR #13 open

**What's blocking:**
- Plan #6 not started: no per-token table with `token_id` + `fingerprint` + passage metadata exists; training runs on raw parallel text only
- Plan #7c (HALOT grammar classifier): **NEEDS_FIX — structural.** 3,120 entries (47%) have `grammar_normalized=None`; only 298 of ~1,500+ expected verbs classified. Investigation Builder dispatched on `fix/halot-grammar-investigation`. Plan #6 blocked on HALOT side until resolved.
- Plan #7a (BDAG GK/Greek Mounce): 0% — not a Hebrew blocker; deferred to Greek track
- No model trained at scale; no rubric metric result; chrF baseline unknown
- Rust export path (Phase 5) not designed

**What's next (Director's recommendation):**
Investigation Builder on `fix/halot-grammar-investigation` delivers `docs/audits/halot-grammar-investigation.md`. After investigation lands, Team Lead surfaces tier classification (Tier 1 mechanical vs Tier 2 interpretation) and estimated fix scope to user. If Tier 1 and small/medium scope, Director round 5 briefs a fix Builder. If fix is similar in size to BDB PR #8, approximately 1–2 rounds to close. Plan #6 follows.

---

## Open questions

**Active (round 4 in-flight):**
- What is the actual HALOT binary format issue causing 47% `grammar=None`? Leading hypothesis: the `extract_grammar` → `pattern_list` scan is constrained by the body-field split logic, placing the `vb.` grammar token outside the scanned text window for ~3,120 entries. Alternative hypotheses: Aramaic/Hebrew section split in the binary, format-version difference between entry types, or `halot_line` field_split strategy dropping grammar-bearing tokens before the body window. Investigation Builder will determine which.
- Is the fix Tier 1 (mechanical — add/fix patterns or scan range) or Tier 2 (interpretation needed — section-boundary logic requires editorial judgment)? Tier classification determines whether Director round 5 can issue a fix brief directly or must surface to user first.
- Does `docs/domain-knowledge-cache.md` HALOT section need extension with structural binary format info (Aramaic section markers, entry-type boundary bytes)? Investigation Builder will answer; Director will update cache after.

**Cross-repo PR coordination:**
- autoresearch PR #13 (BDB close-out): pending merge. No new blocking dependency — fellwork-api PR #8 already on main at `43612c3`. Merge when ready.

**For user (deferred — not blocking immediate work):**
- Confirm Plan #6 corpus assembly schema: should `passage_id` be verse-level (e.g., `Gen.1.1`) or passage-level (pericopae blocks)? This determines how the passage_metadata table keys.
- Confirm whether `genesis_full` (all 1,532 verses) or just Genesis 1–3 fixture is the intended training corpus for the first model run.
- HALOT and BDB both have Hebrew-side coverage; KM is the Greek Mounce lexicon and also contains Hebrew cross-refs via `gk H{n}` pattern. Confirm: for Plan #6 Hebrew-track corpus, are KM's Hebrew cross-references in scope for token augmentation, or only HALOT/BDB?

**Resolved (retired):**
- `docs/domain-knowledge-cache.md` existence question: NOW EXISTS (PR #16). BDB-specific patterns section present and updated with 4 new subsections. Builder briefs reference it directly.
- BDB binyan structural blocker: RESOLVED. 99.3%; fellwork-api PR #8 merged (`43612c3`); autoresearch PR #13 open. Does not block Plan #6.
- #7c stale-baseline question: RESOLVED — defect is real (NEEDS_FIX confirmed by Verifier-3, not stale).
