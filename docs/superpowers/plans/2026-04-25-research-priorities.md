# Research Priorities Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `## Research priorities` section to `program.md` plus a setup-step amendment that introduces `learnings.md` as a per-branch reasoning log.

**Architecture:** Documentation-only change. Two coupled edits to a single file (`program.md`). No new tracked files; `learnings.md` is created by the agent at branch setup time, not committed to the repo.

**Tech Stack:** Markdown. No tests, no code runtime.

**Source spec:** `docs/superpowers/specs/2026-04-25-research-priorities-design.md`

---

## File Structure

Files modified:
- `program.md` (modify) — insert new section between existing `## Experimentation` and `## Output format` headings; amend existing setup step 5.

Files **not** created:
- `learnings.md` is intentionally untracked. The agent creates it during the per-branch setup checklist (matching how `results.tsv` is created today).

---

### Task 1: Add Research priorities section and amend setup step 5 in `program.md`

**Files:**
- Modify: `program.md` (two edits, one commit)

- [ ] **Step 1: Verify the current state of `program.md`**

Run:
```bash
grep -n "^## " program.md
```

Expected output:
```
3:## Setup
22:## Experimentation
42:## Output format
64:## Logging results
90:## The experiment loop
```

If headings are at different line numbers, adjust the Edit calls below to match — the *content* surrounding each heading is the source of truth, not the line number.

- [ ] **Step 2: Amend setup step 5 to mention `learnings.md`**

Find this exact block in `program.md`:

```markdown
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first run.
```

Replace with:

```markdown
5. **Initialize results.tsv and learnings.md**: Create `results.tsv` with just the header row, and create `learnings.md` containing only `# Learnings` as its first line. Both files are appended to as experiments run.
```

- [ ] **Step 3: Insert the new `## Research priorities` section**

Find this exact block in `program.md` (the boundary between Experimentation and Output format):

```markdown
**Crashes**: If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on.

## Output format
```

Replace with (note: insert the entire new section between the "Crashes" paragraph and the existing `## Output format` heading; the trailing `## Output format` line is preserved unchanged):

````markdown
**Crashes**: If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on.

## Research priorities

The goal is **disciplined, interpretable progress on val_bpb**. Each branch should be a readable trail of validated wins, not a stack of un-attributable changes.

### Process discipline

- **One change per experiment.** Two changes at once make deltas un-attributable. Run them as separate experiments and stack the wins.
- **Hypothesis before run.** Write the expected direction and rough magnitude in `learnings.md` *before* `uv run train.py`. If the result surprises you, that itself is a signal — record it.
- **Simplicity tiebreaker.** Equal-or-better val_bpb with less code wins. Deletions that don't hurt are top-tier outcomes.
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

- **Peak VRAM ≤ 10.5 GB.** Watch `peak_vram_mb` in `run.log`; anything above this rolls back the experiment regardless of val_bpb.
- **No new dependencies.** Anything outside `pyproject.toml` is off-limits.
- **Don't touch `prepare.py`.** Constants, dataloader, and `evaluate_bpb` are fixed.
- **Each run completes in ≤ 7 minutes wall-clock.** 5-min training budget + setup/eval. Anything longer = kill and discard.
- **Eager-only runtime.** Don't re-enable `torch.compile`; this fork's runtime path is intentional.

### Anti-patterns

- Don't disable activation checkpointing on profiles where autotune chose it on — you will OOM mid-run.
- Don't combine a Tier 1 and Tier 2 change in one experiment.
- Don't introduce dropout or other stochastic regularization without first showing a baseline overfit; short runs rarely overfit.
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

## Output format
````

- [ ] **Step 4: Verify the edit applied cleanly**

Run:
```bash
grep -n "^## " program.md
```

Expected: a new `## Research priorities` heading appears between `## Experimentation` and `## Output format`, and `## Output format` is still present (unchanged):
```
3:## Setup
22:## Experimentation
42:## Research priorities
... (more lines)
NN:## Output format
NN:## Logging results
NN:## The experiment loop
```

(Exact line numbers depend on insertion size — only the *order* matters.)

Also verify subheadings:
```bash
grep -n "^### " program.md
```

Expected to include the new subheadings:
```
### Process discipline
### Leverage tiers — bias toward Tier 1 first
### Hard constraints (do not break)
### Anti-patterns
### `learnings.md` — entry per experiment
```

- [ ] **Step 5: Sanity-check that all referenced symbols exist in `train.py`**

The new section references constants and functions in `train.py`. Verify each one resolves:

```bash
grep -nE "^WARMUP_RATIO|^WARMDOWN_RATIO|^FINAL_LR_FRAC|^MATRIX_LR|^EMBEDDING_LR|^UNEMBEDDING_LR|^SCALAR_LR|^WEIGHT_DECAY|^ADAM_BETAS|^TOTAL_BATCH_SIZE|^DEPTH|^ASPECT_RATIO|^WINDOW_PATTERN|^HEAD_DIM" train.py
```

Expected: every constant listed appears at the top level of `train.py`.

```bash
grep -n "def get_muon_momentum" train.py
grep -n "def init_weights" train.py
grep -n "n_kv_head" train.py
grep -n "resid_lambdas\|x0_lambdas" train.py
```

Expected: each query returns at least one match. If any reference is missing, the priorities section names a symbol that doesn't exist — fix the section text to match `train.py` rather than the other way around.

- [ ] **Step 6: Verify nothing else changed**

Run:
```bash
git diff --stat program.md
```

Expected: `program.md` is the only modified file, with insertions roughly proportional to the new section size.

```bash
git diff program.md
```

Read the diff. Confirm:
- The new section appears between Experimentation and Output format
- Setup step 5 now mentions `learnings.md`
- Nothing outside those two areas changed

- [ ] **Step 7: Commit**

```bash
git add program.md
git commit -m "$(cat <<'EOF'
docs(program): add research priorities section and learnings.md amendment

Adds a `## Research priorities` section that biases the autonomous research
loop toward disciplined, interpretable progress: one change per experiment,
hypothesis-first, simplicity tiebreaker, 3-miss area-rotation rule. Two-tier
area guidance (Tier 1: low-risk high-leverage knobs; Tier 2: architecture
and higher-risk changes). 10.5 GB peak VRAM ceiling.

Setup step 5 now also creates `learnings.md` per branch — the prose
reasoning log that pairs with `results.tsv`.

Spec: docs/superpowers/specs/2026-04-25-research-priorities-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

Run `git log -1 --format='%s'` to confirm the commit landed.

---

## Verification

This is documentation; there are no automated tests. Verification is by inspection:

1. Re-read `program.md` end-to-end. The new section should read in the same voice as the rest of the file.
2. Every `train.py` symbol the section references must actually exist (Step 5 above).
3. Existing sections (`## Setup`, `## Experimentation`, `## Output format`, `## Logging results`, `## The experiment loop`) must be unchanged except for the one bullet in Setup step 5.

## Spec Coverage

- ✅ `## Research priorities` section inserted between Experimentation and Output format (Step 3)
- ✅ Process discipline sub-block (Step 3)
- ✅ Leverage tiers sub-block with Tier 1 / Tier 2 split (Step 3)
- ✅ Hard constraints with 10.5 GB ceiling (Step 3)
- ✅ Anti-patterns (Step 3)
- ✅ `learnings.md` entry format (Step 3)
- ✅ Setup step 5 amendment for `learnings.md` (Step 2)
- ✅ `learnings.md` left untracked, created per-branch by agent (no Step required — absence of action is the implementation)

No spec requirements unaccounted for.
