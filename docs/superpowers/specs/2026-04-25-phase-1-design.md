# Phase 1: Hebrew→English ML Research Platform — Design Spec

**Date:** 2026-04-25 (revised 2026-04-26 to drop fellwork-api integration from Phase 1)
**Branch context:** master
**Inputs:**
- `gold/catalog.json` (95 entries) — user's preferred translations, extracted from teaching PDFs + Psalm 16
- `gold/rubric.md` (15 patterns) — distinctive translation conventions vs mainstream English
- Public open-source structural data: OSHB (Hebrew + ETCBC morphology), Macula Hebrew (phrase alignments)

**Architectural note:** The existing `fellwork-api` Rust pipeline is **not** a runtime dependency for this research. fellwork-api is downstream of this work — it will be rebuilt later informed by the model, rubric, and validated patterns produced here. Earlier drafts assumed a JSON bridge from fellwork-api → autoresearch; that has been dropped (`docs/bridge-design.md` is preserved as a future-option reference, not a Phase 1 deliverable).

## Problem

Existing English Bible translations make compromises: literal renderings (YLT) preserve Hebrew structure but produce stilted English; dynamic equivalents (NIV/ESV) read fluently but flatten Hebrew structural patterns. Neither captures both *intent preservation* and *natural English coherence*. The user's 95 gold-corpus translations articulate what "correct" looks like; the rubric encodes 15 measurable distinctions between gold and mainstream renderings.

**Phase 1's job is to build a measurement and ML-training platform** so subsequent phases can iteratively close the gap between mainstream output and gold using the autoresearch loop. Phase 1 produces no production translation — it produces the rails.

## Approach

A standalone Hebrew→English seq2seq model trained on multi-reference public-domain translations and evaluated against the gold corpus by chrF + rubric-derived structural checks.

```
Hebrew (OSHB)  +  morphology (ETCBC)  +  phrase nodes (Macula)
                              │
                              ▼
                   prepare_translate.py
                   joins references and gold
                              │
                              ▼
              Multi-reference English (Berean / WEB / YLT)
                              │
                              ▼
                   train_translate.py
                   (Phase 2 designs and tunes the model)
                              │
                              ▼
              evaluate_translate.py — chrF + structural rubric checks
                              │
                              ▼
                  single-scalar score for autoresearch loop
```

## Decisions

| Decision | Choice | Source |
|---|---|---|
| Source language | Hebrew (Greek transfers in a later phase) | User's primary research focus |
| ML role | Standalone seq2seq translator; fellwork-api is **not** a runtime dependency | User clarification 2026-04-26 |
| Bulk training data | Berean + WEB + YLT, multi-reference per verse, joined with OSHB morphology + Macula phrase nodes | Public-domain coverage at corpus scale |
| Gold corpus | `gold/catalog.json` — 95 entries (67 Genesis, 10 Psalms, 15 NT cross-refs, 3 Other-OT) | Extracted from `gold/` PDFs + Psalm 16 image |
| Eval strategy | Leave-one-out cross-validation on Genesis subset (67) + 10–15 holdout test entries reserved | 95 entries is too small for a fixed 60/20/15 split |
| Primary metric | `1 - chrF(candidate, gold)` against held-out gold verse | Standard, single-scalar, lower-better |
| Structural metric | Weighted sum of rubric P1, P3, P4, P6, P8, P10, P12 violations (the 7 highly-automatable patterns from `gold/rubric.md`) | Captures user's distinctive conventions |
| Combined metric | `score = α · (1 − chrF) + (1 − α) · structural_penalty`, with α ≈ 0.5 initially | Tunable; later experiments can ablate |
| Tokenizer | Multilingual BPE with structural special tokens (`<phrase>`, `<clause>`, `<construct>`, suffix tags), vocab ~16k | Two scripts + tag inventory |

## Data sources (public, open-license)

| Component | Source | Format | License |
|---|---|---|---|
| Hebrew text | OSHB (Open Scriptures Hebrew Bible) | OSIS XML on GitHub | Public |
| Morphology | OSHB (ETCBC tags) | Embedded in OSHB OSIS | Public |
| Phrase boundaries | Macula Hebrew (clear.bible) | TSV/JSON treebank | Open |
| English bulk | Berean Standard Bible (BSB) | JSON / plain text | Open |
| English bulk | World English Bible (WEB) | JSON / plain text | Public |
| English bulk | Young's Literal Translation (YLT) | Plain text | Public |
| Gold target | `gold/catalog.json` | Already in repo | User's material |

`prepare_translate.py` is responsible for fetching, parsing, and joining these sources into per-verse training records. Each record carries: Hebrew tokens with morphology, phrase nodes, three reference English strings, and (for gold-set entries) the gold target.

## Eval split

| Bucket | Count | Use |
|---|---|---|
| Bulk train | ~24 K verses × 3 references ≈ 72 K pairs | Pre-train; gold *never* leaks here |
| Fine-tune (gold-train) | 60 entries | Optional fine-tune toward gold style (Phase 3+) |
| LOO dev | 20 entries (rotated through fine-tune as held-out) | Dev signal during autoresearch experiments |
| Holdout test | 15 entries (Psalm 16 + selected high-confidence Genesis) | Reserved; reported once at end of Phase 5 |

Initial Phase 2 baseline runs **without fine-tune**, just bulk-trained — establishes how far the model gets from public-domain references alone. Phase 3+ adds fine-tune on gold.

## Phase 1 deliverables

1. ✅ `gold/catalog.json` — done
2. ✅ `gold/rubric.md` — done
3. **`prepare_translate.py`** — Python ingest replacing `prepare.py`'s TinyStories path. Pulls OSHB + Macula + Berean/WEB/YLT directly; joins to a unified per-verse record; trains the multilingual BPE tokenizer.
4. **`evaluate_translate.py`** — chrF + structural metric returning a single scalar (lower-better). Uses gold catalog as reference.
5. **`train_translate.py`** baseline — minimal seq2seq that runs in 5 min on a 4070 12 GB; produces *some* translation; sanity-checked against the eval harness.
6. **Phase 1 smoke test** — end-to-end (prepare → train → eval → score) without crashes; reports a baseline metric number.

Estimated 2–3 weeks of evening/weekend work.

## Out of scope for Phase 1

- Greek (transfers in a later phase; same architecture)
- **Any integration with fellwork-api** (it's downstream of this research, not upstream)
- Production model deployment
- Fine-tune-on-gold experiments (deferred to Phase 3)
- Phrase-aware attention mechanisms (deferred to Phase 4)

## Risks

| Risk | Mitigation |
|---|---|
| 95 gold entries too small; eval variance dominates | Leave-one-out CV; report mean ± std across LOO folds, not point estimates |
| Rubric pattern P2 / P13 require statistical baselines | Compute against bulk training corpus; defer if metric is noisy |
| Public-source ingestion (OSHB / Macula) has unknown integration cost | Time-box `prepare_translate.py` to one week; if any single source proves intractable, document the gap and proceed with what loaded |
| 5-min training budget too small for any meaningful translation signal | Phase 2 will resize the model down (likely 10–30 M params) and accept that early experiments may be exploratory rather than informative |

## Subsequent phase preview

- **Phase 2**: model architecture design (encoder-decoder vs prefix-LM); first runnable training; baseline numbers
- **Phase 3**: fine-tune on gold; rubric-driven loss shaping
- **Phase 4**: phrase-aware attention; structural editing primitives
- **Phase 5**: rubric-targeted improvements; iteration on specific patterns where gold/baseline diverge
- **Phase 6** (optional): Greek transfer
- **Downstream (separate project)**: fellwork-api rebuild informed by Phase 5 outputs (trained model, validated patterns, eval methodology)

Phases 2–5 are where the autoresearch autonomous loop earns its keep. Phase 1 is the rails.

## Verification

Phase 1 is "done" when:
- Phase 1 smoke test (Deliverable 6) runs end-to-end without crashes
- A baseline metric number exists for the LOO eval set
- The user can read the metric output and confirm "yes, this measures what I care about"
