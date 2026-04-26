# Phase 1: Hebrew→English ML Bridge — Design Spec

**Date:** 2026-04-25
**Branch context:** master
**Inputs:**
- `gold/catalog.json` (95 entries) — user's preferred translations, extracted from teaching PDFs + Psalm 16
- `gold/rubric.md` (15 patterns) — distinctive translation conventions vs mainstream English
- `docs/bridge-design.md` — fellwork-api → autoresearch JSON export design
- Existing fellwork-api Rust pipeline (rule-based translation with R1–R8 documented rules)

## Problem

The user maintains a sophisticated rule-based Hebrew→English translation pipeline in `fellwork-api` with explicit rules for morphology, construct chains, pro-drop, phrase preservation, etc. Comparing the rule pipeline output to the user's gold corpus reveals **two classes of gap**: (1) *fluency* — natural English rhythm; (2) *structural* — places where the rules produce the wrong word order, wrong tense, or miss a distinctive convention captured in the rubric.

**Phase 1's job is to build a measurement and ML-training rail** so subsequent phases can iteratively close those gaps using the autoresearch loop. Phase 1 produces no production translation yet; it produces the foundation.

## Approach: Hybrid Trainable Post-Editor

The ML model takes the rule pipeline's *structured output* (English text + morphology + phrase boundaries) as input and produces a refined English translation calibrated to gold. Rules provide regularity; ML learns the residuals. This preserves the user's invested linguistic work while letting the model revise structure when the rules are wrong.

```
Hebrew tokens (OSHB w/ morphology)
        │
        ▼
fellwork-api rule pipeline ─► structured output (text + components + phrase nodes)
        │
        ▼
JSON export (one verse per record, see docs/bridge-design.md)
        │
        ▼
autoresearch (Python): prepare_translate.py + train_translate.py
        │
        ▼
ML refinement model (Phase 2 will design and tune this)
        │
        ▼
Refined English ─► evaluated against gold by chrF + 8 measurable rubric patterns
```

## Decisions

| Decision | Choice | Source |
|---|---|---|
| Source language | Hebrew (Greek transfers in a later phase) | User's primary research focus |
| ML role | Post-editor on rule output (not replacement) | Brainstorming Q4 → "structural + fluency gaps" |
| Bulk training data | Berean + WEB + YLT, multi-reference per verse, joined with rule-pipeline structural features | Public-domain coverage at corpus scale |
| Gold corpus | `gold/catalog.json` — 95 entries (67 Genesis, 10 Psalms, 15 NT cross-refs, 3 Other-OT) | Extracted from `gold/` PDFs + Psalm 16 image |
| Eval strategy | Leave-one-out cross-validation on Genesis subset (67) + 10–15 holdout test entries reserved | 95 entries is too small for a fixed 60/20/15 split |
| Primary metric | `1 - chrF(candidate, gold)` against held-out gold verse | Standard, single-scalar, lower-better |
| Structural metric | Weighted sum of rubric P1, P3, P4, P6, P8, P10, P12 violations (the 7 highly-automatable patterns from `gold/rubric.md`) | Captures user's distinctive conventions |
| Combined metric | `score = α · (1 − chrF) + (1 − α) · structural_penalty`, with α ≈ 0.5 initially | Tunable; later experiments can ablate |
| Bridge | New `fw-export-ml` binary crate writing JSONL | `docs/bridge-design.md` (~10 hours) |
| Tokenizer | Multilingual BPE with structural special tokens (`<phrase>`, `<clause>`, `<construct>`, suffix tags), vocab ~16k | Two scripts + tag inventory |

## Data contract (summary; full schema in `docs/bridge-design.md`)

Each verse exports as one JSONL record with: canonical ref; Hebrew tokens (surface + lemma + morphology + position); phrase structure (clause nodes, role labels, indent); rule-pipeline output (English text + `TranslationComponents` + `applied_layers`); provenance (schema version, generator commit, timestamp).

The Python ingest (`prepare_translate.py`) joins each verse with its multi-reference English (Berean/WEB/YLT) and, where present, gold target.

## Eval split

| Bucket | Count | Use |
|---|---|---|
| Bulk train | ~24 K verses × 3 references ≈ 72 K pairs | Pre-train; gold *never* leaks here |
| Fine-tune (gold-train) | 60 entries | Optional fine-tune toward gold style |
| LOO dev | 20 entries (rotated through fine-tune as held-out) | Dev signal during autoresearch experiments |
| Holdout test | 15 entries (Psalm 16 + selected high-confidence Genesis) | Reserved; reported once at end of Phase 5 |

Initial Phase 2 baseline runs **without fine-tune**, just bulk-trained — establishes how far the post-editor gets from rules alone. Phase 3+ adds fine-tune.

## Phase 1 deliverables

1. ✅ `gold/catalog.json` — done
2. ✅ `gold/rubric.md` — done
3. ✅ `docs/bridge-design.md` — done
4. **Schema migration** in `fellwork-api`: add `layers_applied jsonb` to `resolved_tokens` (per bridge-design risk callout)
5. **`fw-export-ml` Rust binary** — produces JSONL export
6. **`prepare_translate.py`** — Python ingest replacement for `prepare.py`'s TinyStories path; reads JSONL, joins multi-reference English, builds tokenizer
7. **`evaluate_translate.py`** — chrF + structural metric; returns single scalar
8. **`train_translate.py`** baseline — minimal seq2seq that runs in 5 min on 4070 12 GB; produces *some* translation; sanity-checked against eval harness
9. **Phase 1 smoke test**: end-to-end (export → ingest → train → eval → score) without crashes

Items 4–9 are the build-out work. Estimated 4–6 weeks of evening/weekend work.

## Out of scope for Phase 1

- Greek (transfers in a later phase using same architecture)
- Modifications to `fellwork-api` rule logic itself (only adds export, no rule changes)
- Production model deployment
- Fine-tune-on-gold experiments (deferred to Phase 3)
- Phrase-aware attention mechanisms (deferred to Phase 4)

## Risks

| Risk | Mitigation |
|---|---|
| 95 gold entries too small; eval variance dominates | Leave-one-out CV; report mean ± std across LOO folds, not point estimates |
| Rubric pattern P2 / P13 require statistical baselines | Compute against bulk training corpus; defer if metric is noisy |
| Bridge schema misses a field needed downstream | Schema is versioned; can add fields without invalidating exports |
| 5-min training budget too small for any meaningful translation signal | Phase 2 will resize the model down (likely 10–30 M params) and accept that early experiments may be exploratory rather than informative |
| `applied_layers` is ephemeral in current rule code | Bridge-design calls out this fix; included as Deliverable 4 |

## Subsequent phase preview

- **Phase 2**: model architecture design (encoder-decoder vs prefix-LM); first runnable training; baseline numbers
- **Phase 3**: fine-tune on gold; rubric-driven loss shaping
- **Phase 4**: phrase-aware attention; structural editing primitives
- **Phase 5**: rubric-targeted improvements; iteration on specific patterns where gold/baseline diverge
- **Phase 6** (optional): Greek transfer

Phases 2–5 are where the autoresearch autonomous loop earns its keep. Phase 1 is the rails.

## Verification

Phase 1 is "done" when:
- Phase 1 smoke test (Deliverable 9) runs end-to-end without crashes
- A baseline metric number exists for the LOO eval set
- The user can read the metric output and confirm "yes, this measures what I care about"
