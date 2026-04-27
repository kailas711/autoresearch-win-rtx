"""
Walking-skeleton training: tiny prefix-LM that learns Hebrew->English on
80 verses of Genesis 1-3 in <2 minutes.

Architecture: ~1M-param decoder-only transformer. Sequence is
  [BOS] <hebrew> [SEP] <english> [EOS]
Loss is computed over the full sequence (cross-entropy, ignoring pad).

Usage:
    uv run python train_translate.py             # ~120s skeleton run
    uv run python train_translate.py --smoke-test  # ~30s smoke run
"""
import argparse
import os
import pickle
import random
import struct
import time
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

SMOKE_BUDGET_SEC = 30
FULL_BUDGET_SEC = 120
CORPUS_CHOICES = ("gen_1_3", "genesis_full")


def corpus_name() -> str:
    name = os.environ.get("WALKING_SKELETON_CORPUS", "gen_1_3")
    if name not in CORPUS_CHOICES:
        raise ValueError(f"Unknown corpus {name!r}; expected one of {CORPUS_CHOICES}")
    return name


def cache_dir() -> Path:
    explicit = os.environ.get("WALKING_SKELETON_CACHE")
    if explicit:
        return Path(explicit)
    return Path("data/cache") / corpus_name()


@dataclass
class Config:
    vocab_size: int
    n_layer: int = 4
    n_head: int = 4
    n_embd: int = 128
    block_size: int = 256
    dropout: float = 0.0


def load_shards(path: Path) -> list[list[int]]:
    out = []
    with open(path, "rb") as f:
        while True:
            ln_bytes = f.read(4)
            if not ln_bytes:
                break
            (ln,) = struct.unpack("<I", ln_bytes)
            ids = list(struct.unpack(f"<{ln}I", f.read(4 * ln)))
            out.append(ids)
    return out


class TinyTransformer(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        layer = nn.TransformerEncoderLayer(
            d_model=cfg.n_embd,
            nhead=cfg.n_head,
            dim_feedforward=4 * cfg.n_embd,
            dropout=cfg.dropout,
            batch_first=True,
            norm_first=True,
            activation="gelu",
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=cfg.n_layer)
        self.ln = nn.LayerNorm(cfg.n_embd)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device).unsqueeze(0)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        mask = nn.Transformer.generate_square_subsequent_mask(t, device=idx.device)
        x = self.blocks(x, mask=mask, is_causal=True)
        x = self.ln(x)
        return self.head(x)


def make_batch(sequences: list[list[int]], pad_id: int, block_size: int, device: str, batch_size: int = 8):
    batch = random.choices(sequences, k=batch_size)
    max_len = min(block_size, max(len(s) for s in batch))
    x = torch.full((len(batch), max_len), pad_id, dtype=torch.long)
    for i, s in enumerate(batch):
        s = s[:max_len]
        x[i, : len(s)] = torch.tensor(s, dtype=torch.long)
    return x.to(device)


def main(smoke_test: bool = False) -> dict:
    cache = cache_dir()
    with open(cache / "tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    pad_id = tokenizer.encode_single_token("<|pad|>")

    train_seqs = load_shards(cache / "train.bin")
    val_seqs = load_shards(cache / "val.bin")
    print(f"train={len(train_seqs)}  val={len(val_seqs)}  vocab={tokenizer.n_vocab}")

    cfg = Config(vocab_size=tokenizer.n_vocab)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = TinyTransformer(cfg).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"model params: {n_params:,}")

    optim = torch.optim.AdamW(model.parameters(), lr=3e-4)
    budget = SMOKE_BUDGET_SEC if smoke_test else FULL_BUDGET_SEC
    t0 = time.time()
    step = 0
    final_loss = float("nan")

    while time.time() - t0 < budget:
        x = make_batch(train_seqs, pad_id, cfg.block_size, device)
        logits = model(x[:, :-1])
        loss = F.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            x[:, 1:].reshape(-1),
            ignore_index=pad_id,
        )
        optim.zero_grad(set_to_none=True)
        loss.backward()
        optim.step()
        final_loss = float(loss.item())
        step += 1
        if step % 25 == 0:
            print(f"step {step}  loss {final_loss:.4f}  elapsed {time.time() - t0:.1f}s")

    print(f"trained {step} steps; final loss {final_loss:.4f}")

    import score_translate
    s = score_translate.score(model=model, tokenizer=tokenizer, gold_subset_only=False)
    print(f"final score (1 - chrF): {s:.6f}")
    return {"final_loss": final_loss, "score": s, "steps": step}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    main(smoke_test=args.smoke_test)
