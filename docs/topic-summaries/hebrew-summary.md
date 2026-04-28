# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 8 — Plan #6 Builder dispatch)
**Active rounds:** 8

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master; the BPE tokenizer trains over Genesis 1–3 (80 verses); a 1M-param prefix-LM runs end-to-end under 2 minutes on the RTX 4070.

All three Hebrew-side lexicons are clean and ready for Plan #6 corpus assembly:

**BDB binyan (closed):** 99.3% coverage (1,683 / 1,695 strict-verb entries). PR #18 merged to master. Paired fellwork-api PR #8 merged. Not a Plan #6 blocker.

**HALOT (Phase 3 closed):** All five PRs merged — #9 (RC1+RC2+RC3 grammar fix), #10 (body-fallback fix recovering 102 of 103 lost entries), #18 (BDB, paired), #19 (six-fix omnibus: circular import, verse-range bug, Strong's suffixes, train improvements), #20 (HALOT fixture regen). Final numbers: 6,631 entries / 1,481 verbs / 0 over-extraction. Cross-repo decoder framework landed in fellwork-api at `a26669d`. autoresearch master at `03551fb`. All data-quality gates closed.

**KM:** iter-4 baseline (10,173 entries; 100% `gk_number` coverage). Acceptable as-is for Plan #6 walking-skeleton assembly; binyan audit deferred until signal demands it.

**Plan #6 spec v3 merged on master (`2566de3`).** The Architect produced a 1,326-line spec (`docs/superpowers/specs/2026-04-28-plan-6-corpus-architecture.md`) with all 3 design corrections + Q3=C clarification applied: Correction 1 (linguistic-match joins, cross_walk_references as non-identity), Correction 2 (translations in own table), Correction 3 (per-token interlinear glosses), Correction 4 / Q3=C (STEPBible restored as primary linguistic source). 14 runnable AC scripts in § G. Builder dispatch (r8 → Builder) is the next action.

**v1 scope:** Genesis-only, ~30K tokens, per-pericope passages (~14 pericopes). Phase-split approach (Path B) adopted: 6 phases across multiple Builder dispatches to isolate defects per phase.

**Data inventory confirmed (r7–r8 audit):**
- `data/fixtures/lex_bdb.json` — 9,433 entries; full field schema including `binyanim`, `strongs`, `gk_number`, `senses`, `headword_consonantal`, `headword_vocalized`, `grammar_normalized`, `homograph_index`, and `_source` provenance keys on every annotated field.
- `data/fixtures/lex_halot.json` — 6,631 entries; same field schema as BDB.
- `data/fixtures/lex_km.json` — 10,173 entries; same field schema.
- `data/fixtures/genesis_full_hebrew.json` — 1,532 verses keyed `Gen.1.1`; value = vocalized Hebrew string per verse (flat string, no per-token decomposition yet).
- `data/fixtures/genesis_full_berean.json` — 1,532 verses, same key format, English string per verse.
- `gold/catalog.json` — 95 entries; fields: `ref_start`, `ref_end`, `translation`, `source_pdf`, `confidence`, `match_notes`, `book_section`, `is_partial`.
- `gold/rubric.md` — 15 patterns.

**Critical gap confirmed:** `genesis_full_hebrew.json` is flat verse strings, not per-token records. No `token_id`, no morphology, no phrase annotations, no lexicon join fields exist in any current fixture. Plan #6 builds that layer from scratch.

---

## What changed in the most recent round

**Architect produced Plan #6 spec v3 (1,326 lines, 14 AC scripts, 9 alternatives, 13 out-of-scope items).** PR #21 merged at master commit `2566de3`. The spec covers: per-token table (§ A), per-passage table (§ B), translations table (§ B'), token_id format (§ C), fingerprint algorithm (§ D), passage grain decision (§ E: per-pericope chosen), sourcing pipeline (§ F: OSHB primary for surface/lemma/morphology; STEPBible primary for lemma_vocalized and cross_walk_references; Macula for phrase tree; linguistic-match joins for lexicon_links), and 14 runnable AC scripts (§ G). Three design corrections were applied post-user-review (linguistic-only fingerprint; translations in own table; per-token interlinear glosses). Q3=C clarification added Correction 4: STEPBible restored as primary linguistic source; Strong's/GK preserved as non-identity cross_walk_references. All 14 AC criteria cited at spec master commit `2566de3`.

**Director r8 routes Plan #6 implementation.** Phase-split decision adopted (Path B, 6 phases). Source data availability assessed: OSHB, STEPBible TSV, and Macula Hebrew require fetching (all public, all fetchable via GitHub clone); Berean, gold, and lex fixtures are immediately available; `.ainter`/`.agloss` are locally available but require parser implementation (v1 best-effort: STEPBible interlinear alone satisfies AC-10 at ≥80% if Accordance parsers not built). No BLOCKER — all critical sources are publicly accessible. Phase 1 Builder dispatch proceeds on branch `feat/plan-6-phase-1-ingest`.

---

## Distance to product goal

**Data-quality gates:** All three Hebrew lexicons clean on master. No blockers to Plan #6.

**After Plan #6 v1 (Genesis corpus, ~30K tokens, per-pericope):** Training pipeline can be revised to consume the structured corpus (`prepare_translate.py` extended or replaced). A baseline model can be trained on v1 corpus; chrF metric established on full Genesis; rubric patterns P1–P15 evaluated against model output.

**Subsequent rounds:**
- Full OT extension (Plan #6 v2): ingest all 39 Hebrew Bible books; sense disambiguation curation pass; `.ainter`/`.agloss` parsers if not completed in v1.
- Plan #6 v2 corpus: Macula discourse boundaries beyond Genesis; author_tradition / era_estimate populated from scholarly sources; literary_devices annotation.
- Training pipeline integration — consume Plan #6 corpus in `prepare_translate.py`; evaluate chrF against gold catalog.
- Greek track scaffolding — gated until first Hebrew model trained on structured corpus. Not in scope until Hebrew baseline is established.

**What's still blocking ML signal:**
- Plan #6 corpus not yet built (per-token table, passage metadata, fingerprint pipeline, lexicon joins).
- No model trained at scale on structured corpus; chrF baseline unknown on full Genesis.
- Rust export path not designed.

---

## Open questions

**Source data availability (r8 assessment):**
- OSHB (`github.com/openscriptures/morphhb`) — fetch required; public MIT; not blocking but Builder must fetch before Phase 1.
- STEPBible TSV (`github.com/STEPBible/STEPBible-Data`) — fetch required; public CC BY; not blocking.
- Macula Hebrew (`github.com/Clear-Bible/macula-hebrew`) — fetch required; public CC BY; not blocking but Phase 3 (pericope segmentation) depends on it; fallback to STEPBible paragraph markers available.
- Accordance `.ainter`/`.agloss` — locally available per spec § F; parser implementation is new code (not blocking Phase 1–4; Phase 5 best-effort; STEPBible interlinear alone can satisfy AC-10).
- Anchor Bible Dictionary — licensing uncertain; v1 mechanical defaults for `author_tradition`/`era_estimate`; not a blocker.

**Phase-split decision (r8):** Path B adopted (6-phase split). Each phase has own Builder dispatch + Verifier audit. Phase 1 = OSHB + STEPBible ingest; Phase 2 = token_id + fingerprint; Phase 3 = Macula + pericope segmentation; Phase 4 = lexicon joins; Phase 5 = interlinear glosses; Phase 6 = translations table. Full AC-1–14 re-run at end.

**Follow-on flags (unblocked, not urgent):**
- Flag 1 — `vol.` headword artifact (36 HALOT entries): filed for `fix/halot-vol-headword` branch; not a Plan #6 blocker.
- Flag 2 — 13 binyanim=None verbs: documented as source-truth in domain-knowledge-cache; not a defect.

**Resolved (retired):**
- BDB binyan structural blocker: RESOLVED. 99.3%; PR #18 merged.
- HALOT Phase 2+3 acceptance: RESOLVED. PASS (calibrated). 1,481 verbs; 0 over-extraction.
- Flag 3 (-103 delta explanation): RESOLVED. PRs #9/#20 merged; delta explained and accepted.
- Plan #6 architecture decisions (5 open in r7): RESOLVED by Architect spec v3 (§ C token_id, § D fingerprint, § E per-pericope, § F sourcing, § H alternatives).
