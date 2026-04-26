"""End-to-end walking skeleton tests."""
from pathlib import Path


def test_prepare_translate_produces_outputs(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()
    cache = tmp_path / "cache"
    assert (cache / "tokenizer.pkl").exists()
    assert (cache / "train.bin").exists()
    assert (cache / "val.bin").exists()
    assert (cache / "train.bin").stat().st_size > 0
    assert (cache / "val.bin").stat().st_size > 0
