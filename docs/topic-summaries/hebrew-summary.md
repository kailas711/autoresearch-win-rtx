# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 6 — Phase 2 calibration ACCEPTED; Plan #6 architecture is r7)
**Active rounds:** 6

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable.

All three Hebrew-side lexicons are in good shape for Plan #6 walking-skeleton assembly:

**BDB binyan (closed):** 99.3% coverage (1,683 / 1,695 strict-verb entries). PR #18 merged to master at `76290af`. Paired fellwork-api PR #8 merged at `43612c3`. BDB does not block Plan #6.

**HALOT grammar (Phase 2 closed, calibrated PASS):** Phase 2 fix (RC1+RC2+RC3) shipped on paired branches; fellwork-api PR #9 open (MERGEABLE). Key numbers:

- Verb pool recovered: 298 → 1,471 (4.9× recovery)
- Recoverable ceiling per binary scan: ~1,453–1,458 entries with binyan markers; +13 = explicit `vb.` with empty bodies (source-truth, not extractable)
- Binyan coverage on verb subset: ~99.1%
- Over-extraction: 0 (Verifier-4 confirmed)
- Sample quality: 9/9 named entries PASS on Verifier-4's acceptance script
- None-grammar rate: 50%; this is HALOT's structural editorial reality — Verifier-4's 10-sample categorization returned 4 derived-nouns + 6 proper-names + 0 unrecognized-pattern; no fixable defect exists in this category
- Calibrated acceptance bars: verb count ≥1,450 (revised from ≥1,500 with binary-evidence ceiling); None-grammar <55% structural floor (revised from <10% with 0/10 unrecognized-pattern categorization)
- Phase 2 verdict: **PASS**

**KM:** Still at iter-4 baseline (100% `gk_number` coverage, not yet binyan-audited). Acceptable as-is for Plan #6 walking-skeleton; revisit if signal insufficient.

**PR #19 merged (master `000e5e2`):** Six fixes — score/train circular import broken; verse-range bug fixed in `score_translate.py`; Strong's alphabetic suffixes preserved; `train.py`/`train_translate.py` minor improvements.

---

## What changed in the most recent round

**Builder shipped HALOT Phase 2 (RC1+RC2+RC3) on paired branches.** autoresearch commits: `c475c19` (fixture regenerated) + `f898c7d` (cherry-picked investigation). fellwork-api PR #9 commits: `462454d`, `fdcbf7c`, `ddf03a7`, `d5064b2`. The Phase 2 fix addresses all three root causes diagnosed in the Phase 1 investigation: RC1 (binyan-stem inference for entries with no `vb.` label), RC2 (Roman numeral headword decoding — `"I "` format extension), RC3 (false-positive `n.` matches from etymological abbreviations via word-boundary anchor).

**Verifier-4 independently confirmed numbers + sample quality + Iron Law** on branch `verify/halot-phase-2` (commit `66dd018`). Verifier recommended ACCEPT_AS_PASS with two calibration revisions: verb target ≥1,500 → ≥1,450 (binary ceiling evidence); None-grammar target <10% → <55% structural floor (10-sample categorization evidence). Three non-blocker follow-on flags raised (vol. headword artifact; 13 binyanim=None verbs; -103 entry delta). Director r6 evaluated the calibration evidence against anti-pattern #1 (target revision), found both revisions evidence-justified, and issued CALIBRATION ACCEPTED + Phase 2 PASS.

---

## Distance to product goal

**Data-quality gates:**
- BDB: DONE (99.3%, PR #18 merged)
- HALOT: DONE (Phase 2 PASS, calibrated; PR #9 pending merge after -103 delta explanation)
- KM: Acceptable as-is for walking-skeleton; not a Plan #6 gate

**Plan #6 corpus assembly is the next major work (r7 architecture round).** Plan #6 = per-token table + per-passage metadata table, with `token_id` (e.g., `Gen.1.1.0`) + `fingerprint` (BLAKE2b-128 over structural fields) per `feedback_token_as_first_class_instance.md`. Per-passage table fields follow `feedback_corpus_dimensions.md` (book, canonical section, author tradition, genre, era, language register, audience, literary devices, manuscript witnesses, cross-canon links). Sources: STEPBible TSV (Strong's↔GK), Sefaria Hebrew text + ETCBC morphology, Macula Hebrew phrase nodes, `.ainter` (CATSS parallel), `.agloss`. Greek track is gated until Greek gold corpus exists; not in scope for r7.

**What's still blocking ML signal:**
- Plan #6 not started (per-token table, passage metadata, fingerprint pipeline)
- No model trained at scale; no rubric metric result; chrF baseline unknown
- Rust export path (Phase 5) not designed

**Next round:** r7 dispatches Architect (Mode 2) for Plan #6 schema design. Builder follows in r8. L-scope, multi-session.

---

## Open questions

**Active (round 6 follow-on flags):**
- **Flag 1 — `vol.` headword artifact (36 entries):** Known defect, pre-existing, outside RC1+RC2+RC3 scope. Filed for separate `fix/halot-vol-headword` branch. Not a Plan #6 blocker.
- **Flag 2 — 13 binyanim=None verbs (source-truth):** Clarified by Team Lead — these are explicit `vb.` entries with empty bodies in the HALOT source binary (editorial entries with grammar marker but no body content). Not a defect. Domain-knowledge-cache note: "explicit-vb-empty-body entries are valid verb classifications but lack extractable binyan content; treat as null-binyan verb in corpus assembly."
- **Flag 3 — -103 entry delta (6,632 → 6,529):** Builder has not explained. Requires explanation before fellwork-api PR #9 close. Likely cause: header-row entries or stub entries correctly excluded by Phase 2 fix. Team Lead to SendMessage Builder for explanation; if benign, merge and proceed.

**Architecture decisions needed for Plan #6:**
- Confirm `passage_id` granularity: per-verse (e.g., `Gen.1.1`) or per-pericope block?
- Confirm training corpus scope: Genesis 1–3 (80 verses) or full Genesis (1,532 verses) for first model run?
- KM Hebrew cross-references: in scope for token augmentation in Plan #6, or only HALOT/BDB?
- Audit KM binyan coverage before Plan #6, or accept iter-4 baseline?

**Cross-repo PR coordination:**
- fellwork-api PR #9 (open, MERGEABLE): -103 delta explanation needed first; then merge; then open autoresearch PR (same pattern as PR #8 → PR #18).

**Resolved (retired):**
- BDB binyan structural blocker: RESOLVED. 99.3%; PR #18 + fellwork-api PR #8 merged.
- HALOT Phase 2 acceptance: RESOLVED. PASS (calibrated). Verb ≥1,450 MET (1,471); None-grammar <55% MET (50%).
- 200-char scan limit / halot_line colon-split hypotheses: ELIMINATED by binary investigation.
- نتן / ראה source gaps: CONFIRMED absent from HALOT binary; documented as known source gaps.
