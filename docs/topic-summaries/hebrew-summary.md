# Topic Summary — Hebrew translation

**Last updated:** 2026-04-27 (round 5 — post-HALOT investigation; Phase 2 Builder brief issued)
**Active rounds:** 5

---

## Current understanding

Phase 1 walking skeleton is shipped and green. The three core modules (`prepare_translate.py`, `score_translate.py`, `train_translate.py`) exist on master, the BPE tokenizer trains over Genesis 1–3 (80 verses), and a 1M-param prefix-LM runs end-to-end in under 2 minutes on the RTX 4070. The loop — prepare → train → score (chrF) — is runnable. This satisfies the Phase 1 walking-skeleton deliverables (#3, #4, #5, #6 per the Phase 1 plan).

Lexicon fixtures are the second major accomplishment. Seven fixture files are committed to `data/fixtures/`: four Accordance-sourced (`lex_halot.json` ~22 MB, `lex_bdag.json` ~38 MB, `lex_bdb_accordance.json` ~1 MB, `lex_km.json` ~25 MB) and three public-domain (`lex_bdb.json` ~38 MB, `lex_lsj.json` ~23 MB, `lex_thayer.json` ~5 MB). Iter-4 data quality fixes (PR #14) materially improved extraction: KM `gk_number` now 100% populated (was 0%); HALOT binyanim now 95.6% on verbs (was 0.1%); BDAG multi-sense parsing now working for 1,908 entries (was 0); BDB clean at 8,846 entries passing G.1. Genesis full corpus (1,532 verses, PR #8/11) is on master with HTML cleanup (PR #11).

The orchestration doc moved to v3 (PR #15), introducing the Topic Director / Synthesizer split. The research loop is now runnable in principle, but two gates block ML signal: (a) Plan #6 corpus assembly (per-token `token_id` + `fingerprint` + multi-dimensional metadata) does not yet exist — the model currently trains on raw Genesis parallel text with no lexicon augmentation; (b) known lexicon defects (Plan #7a/b/c) will degrade corpus quality if left unresolved before assembly. Model training has not been attempted at scale; there are no results in `results.tsv`; the chrF metric is a smoke scaffold only.

**BDB binyan (closed):** BDB binyan coverage is **99.3%** (1,683 / 1,695 strict-verb entries). All 3 sub-defects (227 verb entries with `binyanim=None`; הלך misclassified as noun; עשה absent from fixture) are resolved. PR #18 merged to master at `76290af`. Paired fellwork-api PR #8 merged to main at `43612c3`. BDB does not block Plan #6.

**PR #19 merged (Gemini code-review batch, master `000e5e2`):** Six fixes applied: score/train circular import broken; verse-range bug fixed in `score_translate.py` (was distorting chrF for 47/67 Genesis catalog entries with multi-verse gold ranges); Strong's alphabetic suffixes preserved for Hebrew homographs; minor `train.py` + `train_translate.py` improvements. This is the current master HEAD.

**HALOT Phase 1 investigation (complete on `fix/halot-grammar-investigation` at `859aebf`):** Investigation Builder produced a 339-line doc (`docs/audits/halot-grammar-investigation.md`) with hex evidence from the source binary. Three root causes diagnosed, all Tier 1 mechanical, all small scope:

- **RC1 — Missing `vb.` label in high-frequency verb entries.** ~1,200+ HALOT verb roots omit the `vb.` marker entirely (editorial convention — verbal nature implicit for common roots). Body signals verb identity only through stem section headers (`qal:`, `niphal:`, etc.). Fix: binyan-stem inference rule.
- **RC2 — Roman numeral headword decoding failure.** HALOT uses `"I amr"` format (space, no dot); `is_roman_numeral_stub()` only handles BDB's `"I."` format (dot). 1,294 homograph entries decode to `headword_consonantal=None`. Fix: extend stub check to `"I "` variant.
- **RC3 — False-positive `n.` matches from etymological abbreviations.** Entries get tagged `noun` because `n.` matches substrings in etymological notes (e.g., `"MHb."`, `"OSArb."`). Fix: word-boundary-anchor the pattern match.
- RC1 and RC2 are tightly coupled (same code path); co-dispatch in Phase 2a. RC3 is independent; Phase 2b.
- Both `200-char scan limit` and `halot_line colon-split` hypotheses from r4 were **eliminated** by binary evidence. The `vb.` label is simply absent from high-frequency entries; the scan limit comment is stale documentation.

**Known source gaps confirmed by investigation:** נתן has NO standalone Hebrew verb root entry in the HALOT binary (editorial omission — only Aramaic cognate at entry 7297 and derived nouns). ראה's Hebrew root entry was not locatable; possible editorial omission or unexpected beta-code encoding. Both are excluded from Phase 2 acceptance criteria. Phase 2 Builder will attempt a deeper ראה search.

**Domain-knowledge cache:** `docs/domain-knowledge-cache.md` HALOT section now contains binyan markers and cross-ref patterns (from prior rounds). The investigation doc's addendum section (HALOT Class 1/2 verb formats, Roman numeral prefix distinction, נתן/ראה absence notes) needs to be transferred to the cache by the Phase 2 Builder as part of commit work.

**User decision (2026-04-27):** Proceed with Phase 2 — Builder fix on all 3 root causes on paired branches `fix/halot-grammar-residuals`.

---

## What changed in the most recent round

**Investigation Builder shipped the root-cause doc (339 lines, branch `fix/halot-grammar-investigation`, commit `859aebf`):** Section B produced hex dumps of 5 named verb entries from the HALOT binary. Key finding: the source binary contains NO `vb.` label in any of the high-frequency Hebrew verb entries (אמר 5,280x, עשה 2,627x, ידע 949x, בוא 2,550x). HALOT's editorial convention omits the POS label for roots universally known as verbs. Three root causes diagnosed (RC1+RC2 coupled, RC3 independent). The two prior hypotheses — 200-char body scan limit and `halot_line` colon-split misfiring — were both eliminated by direct binary inspection. The scope is small (1–2 files per RC). This is the same shape as the BDB investigation → fix → verify cycle.

**PR #18 merged (BDB binyan close-out, master `76290af`):** BDB binyan path closed cross-repo. Paired with fellwork-api PR #8 at `43612c3`. The BDB fixture at `data/fixtures/lex_bdb.json` is the regenerated version from the post-fix decoder. No further action required on BDB #7b.

**PR #19 merged (Gemini code-review batch, master `000e5e2`):** Six fixes applied in a single batch. The high-impact item is the verse-range bug in `score_translate.py` — multi-verse gold entries (e.g., `Gen.1.1-2`) were being evaluated as single-verse lookups, distorting chrF scores for 47 of 67 Genesis catalog entries. The fix aligns score evaluation with the actual gold range structure. Additional fixes: `train.py`/`train_translate.py` minor improvements; circular import between score and train modules broken; Strong's homograph suffixes preserved in the fetch pipeline.

---

## Distance to product goal

**What we have:**
- Runnable end-to-end loop (prepare → train → score) on Genesis 1–3 fixture
- Full Genesis corpus (1,532 verses) clean on master
- Seven lexicon fixtures with known quality profile
- Phase 1 walking skeleton passing smoke tests
- Gold corpus at `gold/catalog.json` (95 entries; 67 Genesis-heavy); rubric at `gold/rubric.md` (15 patterns; 7 automatable)
- BDB binyan: **DONE** — 99.3%; PR #18 merged `76290af`; fellwork-api PR #8 merged `43612c3`
- HALOT Phase 1 investigation: **DONE** — 3 RCs diagnosed, all Tier 1 mechanical, small scope

**What's blocking:**
- **Plan #6 not started:** no per-token table with `token_id` + `fingerprint` + passage metadata exists; training runs on raw parallel text only. Unblocks after Phase 2 PASS.
- **HALOT Phase 2 (in progress):** 3 RCs to fix on paired branches `fix/halot-grammar-residuals`. Expected outcome: verb pool 298 → ~1,500+; None-grammar 47% → under 10%. Phase 2 is the last data-quality gate before Plan #6.
- Plan #7a (BDAG GK/Greek Mounce): 0% — deferred to Greek track, not a Hebrew blocker
- No model trained at scale; no rubric metric result; chrF baseline unknown
- Rust export path (Phase 5) not designed

**What's next:**
Phase 2 Builder on `fix/halot-grammar-residuals` (autoresearch) + `fix/halot-grammar-residuals` (fellwork-api), paired. RC1+RC2 in Phase 2a (single commit each); RC3 in Phase 2b. Verifier-4 runs acceptance script after Builder. After Verifier-4 PASS, Director round 6 confirms all data-quality gates and refines Plan #6 architecture brief.

---

## Open questions

**Active (round 5 in-flight):**
- How does the binyan-stem inference rule (RC1 fix) interact with HALOT entries that have stem markers but no other classification signal? Investigation Section D conclusion answers this: the fix fires ONLY when explicit binyan stem labels (`qal:`, `niphal:`, etc.) are present in the body — non-verbs (nouns, adjectives) do not contain these markers, so false positives should be zero. Verifier-4 over-extraction check enforces this (must = 0).
- Does ראה's absence from the HALOT binary resolve to a source-gap (like נתן) or unexpected beta-code encoding? Investigation Section B was unable to locate the root entry. Phase 2 Builder will attempt a targeted binary search; if absent, document as known-source-gap alongside נתן.
- Domain-knowledge cache: investigation addendum (HALOT Class 1/2 verb formats, Roman numeral prefix distinction, נתן/ראה absence notes) not yet transferred to `docs/domain-knowledge-cache.md`. Phase 2 Builder is responsible for this update as part of the fix commit.

**Cross-repo PR coordination:**
- fellwork-api `fix/halot-grammar-residuals` PR must merge first, then autoresearch PR (same merge order as PR #8 → PR #18 pattern).

**For user (deferred — not blocking immediate work):**
- Confirm Plan #6 corpus assembly schema: `passage_id` at verse-level (e.g., `Gen.1.1`) or passage-level (pericopae blocks)?
- Confirm whether `genesis_full` (all 1,532 verses) or just Genesis 1–3 is the intended training corpus for the first model run.
- HALOT and BDB both have Hebrew-side coverage; KM also contains Hebrew cross-refs. For Plan #6 Hebrew-track corpus: are KM's Hebrew cross-references in scope for token augmentation, or only HALOT/BDB?
- KM has not yet been audited for data quality. Confirm: audit KM before Plan #6, or accept current state?

**Resolved (retired):**
- `docs/domain-knowledge-cache.md` existence: NOW EXISTS. BDB-specific patterns section present.
- BDB binyan structural blocker: RESOLVED. 99.3%; PR #18 merged; paired fellwork-api PR #8 merged.
- HALOT scope-determination question: RESOLVED by investigation. 3 RCs, all Tier 1 mechanical, small scope. 200-char scan limit and halot_line colon-split hypotheses eliminated.
- #7c stale-baseline question: RESOLVED — defect real (NEEDS_FIX confirmed by Verifier-3).
