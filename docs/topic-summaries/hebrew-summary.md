# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 7 — HALOT closed; Plan #6 architecture round)
**Active rounds:** 7

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master; the BPE tokenizer trains over Genesis 1–3 (80 verses); a 1M-param prefix-LM runs end-to-end under 2 minutes on the RTX 4070.

All three Hebrew-side lexicons are clean and ready for Plan #6 corpus assembly:

**BDB binyan (closed):** 99.3% coverage (1,683 / 1,695 strict-verb entries). PR #18 merged to master. Paired fellwork-api PR #8 merged. Not a Plan #6 blocker.

**HALOT (Phase 3 closed):** All five PRs merged — #9 (RC1+RC2+RC3 grammar fix), #10 (body-fallback fix recovering 102 of 103 lost entries), #18 (BDB, paired), #19 (six-fix omnibus: circular import, verse-range bug, Strong's suffixes, train improvements), #20 (HALOT fixture regen). Final numbers: 6,631 entries / 1,481 verbs / 0 over-extraction. Cross-repo decoder framework landed in fellwork-api at `a26669d`. autoresearch master at `03551fb`. All data-quality gates closed.

**KM:** iter-4 baseline (10,173 entries; 100% `gk_number` coverage). Acceptable as-is for Plan #6 walking-skeleton assembly; binyan audit deferred until signal demands it.

**Data inventory confirmed (r7 audit):**
- `data/fixtures/lex_bdb.json` — 9,433 entries; full field schema including `binyanim`, `strongs`, `gk_number`, `senses`, `morphology`, `homograph_index`, and `_source` provenance keys on every annotated field.
- `data/fixtures/lex_halot.json` — 6,631 entries; same field schema as BDB.
- `data/fixtures/lex_km.json` — 10,173 entries; same field schema.
- `data/fixtures/genesis_full_hebrew.json` — 1,532 verses keyed `Gen.1.1`; value = vocalized Hebrew string per verse (flat string, no per-token decomposition yet).
- `data/fixtures/genesis_full_berean.json` — 1,532 verses, same key format, English string per verse.
- `gold/catalog.json` — 95 entries; fields: `ref_start`, `ref_end`, `translation`, `source_pdf`, `confidence`, `match_notes`, `book_section`, `is_partial`.
- `gold/rubric.md` — 15 patterns.

**Critical gap confirmed:** `genesis_full_hebrew.json` is flat verse strings, not per-token records. No `token_id`, no morphology, no phrase annotations, no lexicon join fields exist in any current fixture. Plan #6 builds that layer from scratch.

---

## What changed in the most recent round

**Phase 3 closed via five PRs (r5–r6 work).** The HALOT grammar fix (RC1+RC2+RC3) recovered the verb pool from 298 to 1,471 (4.9×). PR #10 added a body-fallback refinement recovering 102 of 103 lost entries; 1 marginal entry remains excluded — acceptable, not a Phase 4 blocker. PR #19 shipped six independent fixes (circular import, verse-range bug, Strong's suffixes, training improvements). PR #20 regenerated the HALOT fixture to 6,631 entries / 1,481 verbs with 0 over-extraction. Verifier-4 independently confirmed all acceptance criteria. Director r6 issued CALIBRATION ACCEPTED + Phase 2 PASS on both calibrated bars (verb ≥1,450, None-grammar <55% structural floor).

**Director r7 (this round) routes Plan #6 architecture.** The Architect brief (§ 5 of `docs/topic-director-notes/hebrew-2026-04-27-r7.md`) specifies a 10-section schema design deliverable covering per-token table, per-passage table, token_id format, fingerprint algorithm, passage grain decision, sourcing pipeline, runnable acceptance criteria, alternatives considered, migration path, and explicit out-of-scope list. Architect produces the spec; Builder implements in r8.

---

## Distance to product goal

**Data-quality gates:** All three Hebrew lexicons clean on master. No blockers to Plan #6.

**Plan #6 is the architectural foundation for actual translation model training.** After Plan #6:

- **r8** — Builder implements corpus assembler: multi-source ingest (OSHB/Sefaria, Macula Hebrew, STEPBible TSV, lexicon fixtures), per-token record generation with `token_id` + BLAKE2b-128 fingerprint, per-passage metadata table, lexicon FK joins. Output: `data/corpus/hebrew/v1.jsonl` + `data/corpus/hebrew/passages.jsonl`.
- **r9** — Verifier audits corpus quality (coverage, fingerprint uniqueness, lexicon-join rates, gold-catalog token presence, passage FK integrity).
- **r10+** — Training loop refactor to consume Plan #6 corpus as primary input; chrF baseline established; rubric metric run.
- **Greek track** — gated until first Hebrew model trained. Not in scope for r7–r10.

**What's still blocking ML signal:**
- Plan #6 corpus not started (per-token table, passage metadata, fingerprint pipeline).
- No model trained at scale; no rubric metric result; chrF baseline unknown on full Genesis.
- Rust export path (Phase 5) not designed.

---

## Open questions

**Architecture decisions Plan #6 must resolve (Architect brief, r7):**

1. **Passage grain:** per-verse (e.g., `Gen.1.1`) vs per-pericope (oratorical/narrative unit per Macula Hebrew discourse boundaries) vs per-chapter? Director preference: per-pericope as primary unit with per-verse FKs for tokens. Architect must choose and justify against all three options.

2. **Multiple-witness representation:** passages with divergent MT / LXX / DSS readings — flag at passage level only, or carry alternate token rows?

3. **Disputed authorship:** JEDP source-criticism positions (Mosaic | J | E | D | P) are contested. Schema must encode competing positions as optional fields without enforcing one.

4. **Cross-canon link grain:** per-verse links (e.g., `Gen.1.1 → John.1.1`) or per-pericope? Both are defensible; Architect decides.

5. **Greek track schema parity:** confirm the same per-token / per-passage schema accommodates NT Greek when that track lights up (different identifier fields: `bdag_key`, `thayer_key`, `lsj_key` instead of `halot_key`/`bdb_key`).

**Follow-on flags (unblocked, not urgent):**
- Flag 1 — `vol.` headword artifact (36 HALOT entries): filed for `fix/halot-vol-headword` branch; not a Plan #6 blocker.
- Flag 2 — 13 binyanim=None verbs: documented as source-truth in domain-knowledge-cache; not a defect.

**Resolved (retired):**
- BDB binyan structural blocker: RESOLVED. 99.3%; PR #18 merged.
- HALOT Phase 2+3 acceptance: RESOLVED. PASS (calibrated). 1,481 verbs; 0 over-extraction.
- Flag 3 (-103 delta explanation): RESOLVED. PRs #9/#20 merged; delta explained and accepted.
