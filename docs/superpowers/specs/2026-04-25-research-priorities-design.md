# Research Priorities for autoresearch — Design Spec

**Date:** 2026-04-25
**Branch context:** master (pre-implementation)
**Target file:** `program.md` (new section) + `learnings.md` (new file template)

## Problem

The default `program.md` gives the agent setup steps, the experiment loop, and the simplicity tiebreaker, but no opinion on *what to try* or *how to track reasoning across runs*. On a single 4070 (12 GB, Ada, profile `ada-10-15gb`, autotune-selected `batch_size=4` with checkpointing), an unguided agent will thrash across unrelated knobs and produce a `results.tsv` whose deltas are hard to interpret in the morning.

We want a `## Research priorities` section that biases the agent toward **disciplined, interpretable progress** without foreclosing creative recombinations.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Run goal | Disciplined / interpretable | User wants to learn what moves val_bpb, not just chase a number |
| Area guidance | Leverage-tiered (Tier 1 / Tier 2) | Sensible search order without rigid phase gating |
| Reasoning log | New parallel `learnings.md` | Prose format for hypothesis → conclusion; doesn't break existing tsv contract |
| Stop-line threshold | 3 consecutive misses in same area | User-confirmed; agent switches tiers/areas after this |
| VRAM ceiling | 10.5 GB peak | Tighter than autotune's 90% (10.8 GB) to leave headroom for under-estimates |

## Content to add to `program.md`

Insert a new `## Research priorities` section between the existing `## Experimentation` and `## Output format` sections. Verbatim content:

````markdown
## Research priorities

The goal is **disciplined, interpretable progress on val_bpb**. Each branch should be a readable trail of validated wins, not a stack of un-attributable changes.

### Process discipline

- **One change per experiment.** Two changes at once make deltas un-attributable. Run them as separate experiments and stack the wins.
- **Hypothesis before run.** Write the expected direction and rough magnitude in `learnings.md` *before* `uv run train.py`. If the result surprises you, that itself is a signal — record it.
- **Simplicity tiebreaker.** Equal-or-better val_bpb with less code wins. Deletions that don't hurt are top-tier outcomes (already in the doc; reinforce here).
- **Stop a line after 3 consecutive misses.** If three experiments in the same area (e.g., LR variants) don't improve val_bpb, switch areas. Don't keep grinding the same knob.
- **Stack wins; don't blend.** Each commit kept on the branch is one validated improvement on top of the previous one. Never stack an unvalidated change on top of an unvalidated change.

### Leverage tiers — bias toward Tier 1 first

**Tier 1 — low-risk, high-leverage.**

- LR schedule: `WARMUP_RATIO`, `WARMDOWN_RATIO`, `FINAL_LR_FRAC`
- Optimizer hyperparameters: `MATRIX_LR`, `EMBEDDING_LR`, `UNEMBEDDING_LR`, `SCALAR_LR`, `WEIGHT_DECAY`, `ADAM_BETAS`
- Muon momentum schedule (`get_muon_momentum`, currently 0.85 → 0.95 over 300 steps)
- Init scales (the `s = 3 ** 0.5 * n_embd ** -0.5` in `init_weights`, the `lm_head` init std = 0.001)
- `TOTAL_BATCH_SIZE` (note: changing this changes `grad_accum_steps`)

**Tier 2 — higher-risk, requires written motivation.**

- `DEPTH` and `ASPECT_RATIO` (depth × width)
- Attention: `n_kv_head` (GQA), `WINDOW_PATTERN`, `HEAD_DIM`
- MLP: activation function (currently ReLU²), expansion ratio (currently 4×)
- Logits softcap (currently 15)
- Value embeddings, residual lambdas (`resid_lambdas`, `x0_lambdas`)
- Normalization variant (currently RMSNorm)

**Rule:** Start every fresh branch in Tier 1. When one Tier 1 area stalls (3 misses), switch to a *different* Tier 1 area before moving up. Move to Tier 2 only after at least two Tier 1 areas have stalled in the same branch, *or* you have a written hypothesis in `learnings.md` that specifically requires a Tier 2 change.

### Hard constraints (do not break)

- **Peak VRAM ≤ 10.5 GB.** Watch `peak_vram_mb` in run.log; anything above this rolls back the experiment regardless of val_bpb.
- **No new dependencies.** Anything outside `pyproject.toml` is off-limits.
- **Don't touch `prepare.py`.** Constants, dataloader, and `evaluate_bpb` are fixed.
- **Each run completes in ≤ 7 minutes wall-clock.** 5-min training budget + setup/eval. Anything longer = kill and discard.
- **Eager-only runtime.** Don't re-enable `torch.compile`; this fork's runtime path is intentional.

### Anti-patterns

- Don't disable activation checkpointing on profiles where autotune chose it on — you will OOM mid-run.
- Don't combine a Tier 1 and Tier 2 change in one experiment.
- Don't introduce dropout or other stochastic regularization without first showing baseline overfit; short runs rarely overfit.
- Don't bring in optimizer libraries; tune `MuonAdamW` instead.
- Don't change anything that lowers val_bpb in ways unrelated to actual modeling (eval-window edits, tokenizer changes, etc).

### `learnings.md` — entry per experiment

Append one entry per experiment, in the same order as `results.tsv`:

```markdown
## <short-commit> — <one-line title>
- Hypothesis: <what we expected and why; cite tier and area>
- Change: <specific lines/symbols modified, e.g. "MATRIX_LR 0.04 → 0.06">
- Observation: <val_bpb delta vs prior best, peak_vram_mb, anything notable in run.log>
- Conclusion: <kept | discarded | crash; why; what to try next>
```

The hypothesis goes in *before* the run; the observation and conclusion go in after. If the experiment crashes, record what was attempted and the failure mode under Observation, then move on.
````

## Setup-step amendment

In the existing `## Setup` section's step 5 (Initialize results.tsv), expand to also create `learnings.md` with a single `# Learnings` header. Suggested wording change:

> 5. **Initialize results.tsv and learnings.md**: Create `results.tsv` with just the header row, and `learnings.md` with `# Learnings` as its only line. Both will be appended to as experiments run.

## Implementation steps

1. Edit `program.md`:
   - Insert the `## Research priorities` section between `## Experimentation` and `## Output format`.
   - Update setup step 5 to mention `learnings.md`.
2. (Optional) Add `learnings.md` as a tracked file in the repo with just `# Learnings` so it shows up immediately on fresh checkouts. Alternatively, leave it un-tracked and let the agent create it during setup. Recommendation: leave it untracked since `results.tsv` is also created fresh per branch.
3. Verify the edited `program.md` renders correctly (no broken markdown).

## Out of scope

- Changes to `train.py`, `prepare.py`, or any actual code behavior.
- Adding hooks/scripts to enforce the rules programmatically. Enforcement is by agent compliance, same as today.
- A separate machine-readable schema for `learnings.md`. Markdown is sufficient; agents and humans can both read it.

## Verification

This is a documentation change. Verification is a re-read pass:
- `program.md` renders without broken sections after the insertion.
- The new section uses the same heading style and prose voice as the rest of the file.
- All knob names referenced (`MATRIX_LR`, `WARMUP_RATIO`, etc.) match the current `train.py` constants.
