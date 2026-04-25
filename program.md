# autoresearch

This is an experiment to have the LLM do its own research.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `README.md` — repository context.
   - `prepare.py` — fixed constants, data prep, tokenizer, dataloader, evaluation. Do not modify.
   - `train.py` — the file you modify. Model architecture, optimizer, training loop.
4. **Verify data exists**: Check that `~/.cache/autoresearch/` contains data shards and a tokenizer. If not, tell the human to run `uv run prepare.py`.
5. **Initialize results.tsv and learnings.md**: Create `results.tsv` with just the header row, and create `learnings.md` containing only `# Learnings` as its first line. Both files are appended to as experiments run.
6. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs on a single GPU. The training script runs for a **fixed time budget of 5 minutes** (wall clock training time, excluding startup/compilation). You launch it simply as: `uv run train.py`.

**What you CAN do:**
- Modify `train.py` — this is the only file you edit. Everything is fair game: model architecture, optimizer, hyperparameters, training loop, batch size, model size, etc.

**What you CANNOT do:**
- Modify `prepare.py`. It is read-only. It contains the fixed evaluation, data loading, tokenizer, and training constants (time budget, sequence length, etc).
- Install new packages or add dependencies. You can only use what's already in `pyproject.toml`.
- Modify the evaluation harness. The `evaluate_bpb` function in `prepare.py` is the ground truth metric.

**The goal is simple: get the lowest val_bpb.** Since the time budget is fixed, you don't need to worry about training time — it's always 5 minutes. Everything is fair game: change the architecture, the optimizer, the hyperparameters, the batch size, the model size. The only constraint is that the code runs without crashing and finishes within the time budget.

**VRAM** is a soft constraint. Some increase is acceptable for meaningful val_bpb gains, but it should not blow up dramatically.

**Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A 0.001 val_bpb improvement that adds 20 lines of hacky code? Probably not worth it. A 0.001 val_bpb improvement from deleting code? Definitely keep. An improvement of ~0 but much simpler code? Keep.

**The first run**: Your very first run should always be to establish the baseline, so you will run the training script as is.

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

Once the script finishes it prints a summary like this:

```
---
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
```

Note that the script is configured to always stop after 5 minutes, so depending on the computing platform of this computer the numbers might look different. You can extract the key metric from the log file:

```
grep "^val_bpb:" run.log
```

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated — commas break in descriptions).

The TSV has a header row and 5 columns:

```
commit	val_bpb	memory_gb	status	description
```

1. git commit hash (short, 7 chars)
2. val_bpb achieved (e.g. 1.234567) — use 0.000000 for crashes
3. peak memory in GB, round to .1f (e.g. 12.3 — divide peak_vram_mb by 1024) — use 0.0 for crashes
4. status: `keep`, `discard`, or `crash`
5. short text description of what this experiment tried

Example:

```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autoresearch/mar5` or `autoresearch/mar5-gpu0`).

LOOP FOREVER:

1. Look at the git state: the current branch/commit we're on
2. Tune `train.py` with an experimental idea by directly hacking the code.
3. git commit
4. Run the experiment: `uv run train.py > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
5. Read out the results: `grep "^val_bpb:\|^peak_vram_mb:" run.log`
6. If the grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the Python stack trace and attempt a fix. If you can't get things to work after more than a few attempts, give up.
7. Record the results in the tsv
8. If val_bpb improved (lower), you "advance" the branch, keeping the git commit
9. If val_bpb is equal or worse, you git reset back to where you started

The idea is that you are a completely autonomous researcher trying things out. If they work, keep. If they don't, discard. And you're advancing the branch so that you can iterate. If you feel like you're getting stuck in some way, you can rewind but you should probably do this very very sparingly (if ever).

**Timeout**: Each experiment should take ~5 minutes total (+ a few seconds for startup and eval overhead). If a run exceeds 10 minutes, kill it and treat it as a failure (discard and revert).

**Crashes**: If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on.

**NEVER STOP**: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep, or gone from a computer and expects you to continue working *indefinitely* until you are manually stopped. You are autonomous. If you run out of ideas, think harder — read papers referenced in the code, re-read the in-scope files for new angles, try combining previous near-misses, try more radical architectural changes. The loop runs until the human interrupts you, period.

As an example use case, a user might leave you running while they sleep. If each experiment takes you ~5 minutes then you can run approx 12/hour, for a total of about 100 over the duration of the average human sleep. The user then wakes up to experimental results, all completed by you while they slept!
