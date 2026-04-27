"""
Data preparation for Hebrew->English translation.

Reads data/fixtures/<corpus>_{hebrew,berean}.json, trains a small BPE
tokenizer over the combined corpus, encodes each verse pair as a
prefix-LM sequence, writes binary shards to a cache directory.

Corpus selection via WALKING_SKELETON_CORPUS env var:
- gen_1_3 (default) -- 80 verses, walking-skeleton fixtures
- genesis_full -- 1532 verses, full Genesis 1-50 (Sefaria + Berean)

Each sequence: [BOS] <hebrew tokens> [SEP] <english tokens> [EOS]

Usage:
    uv run python prepare_translate.py
    WALKING_SKELETON_CORPUS=genesis_full uv run python prepare_translate.py
"""
import json
import os
import pickle
import struct
from pathlib import Path

import rustbpe
import tiktoken

VOCAB_SIZE = 4096
SPECIAL = ["<|bos|>", "<|sep|>", "<|eos|>", "<|pad|>"]
SPLIT_PATTERN = (
    r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|"""
    r"""\p{N}{1,2}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
)
FIXTURES = Path("data/fixtures")
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


def load_fixtures():
    name = corpus_name()
    he = json.loads((FIXTURES / f"{name}_hebrew.json").read_text(encoding="utf-8"))
    en = json.loads((FIXTURES / f"{name}_berean.json").read_text(encoding="utf-8"))
    assert set(he.keys()) == set(en.keys()), "Hebrew/English ref keys must match"
    refs = sorted(he.keys(), key=lambda r: tuple(int(p) for p in r.split(".")[1:]))
    return [(r, he[r], en[r]) for r in refs]


def train_tokenizer(pairs):
    raw = rustbpe.Tokenizer()
    raw.train_from_iterator(
        (text for _, h, e in pairs for text in (h, e)),
        VOCAB_SIZE - len(SPECIAL),
        pattern=SPLIT_PATTERN,
    )
    mergeable = {bytes(k): v for k, v in raw.get_mergeable_ranks()}
    offset = len(mergeable)
    specials = {name: offset + i for i, name in enumerate(SPECIAL)}
    return tiktoken.Encoding(
        name="walking_skeleton",
        pat_str=raw.get_pattern(),
        mergeable_ranks=mergeable,
        special_tokens=specials,
    )


def encode_pair(enc, hebrew, english):
    bos = enc.encode_single_token("<|bos|>")
    sep = enc.encode_single_token("<|sep|>")
    eos = enc.encode_single_token("<|eos|>")
    he_ids = enc.encode_ordinary(hebrew)
    en_ids = enc.encode_ordinary(english)
    return [bos] + he_ids + [sep] + en_ids + [eos]


def write_shard(path: Path, sequences: list[list[int]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        for seq in sequences:
            f.write(struct.pack("<I", len(seq)))
            f.write(struct.pack(f"<{len(seq)}I", *seq))


def main():
    out = cache_dir()
    out.mkdir(parents=True, exist_ok=True)

    print(f"Corpus: {corpus_name()}")
    pairs = load_fixtures()
    print(f"Loaded {len(pairs)} verse pairs")

    enc = train_tokenizer(pairs)
    print(f"Trained tokenizer: vocab={enc.n_vocab}")

    with open(out / "tokenizer.pkl", "wb") as f:
        pickle.dump(enc, f)

    sequences = [encode_pair(enc, h, e) for _, h, e in pairs]
    split = max(1, len(sequences) // 10)
    val = sequences[:split]
    train = sequences[split:]

    write_shard(out / "train.bin", train)
    write_shard(out / "val.bin", val)

    print(f"Wrote {len(train)} train + {len(val)} val sequences to {out}")


if __name__ == "__main__":
    main()
