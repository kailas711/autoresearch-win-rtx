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


def test_score_translate_returns_scalar(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()

    import score_translate
    s = score_translate.score(model=None, tokenizer=None, gold_subset_only=True)
    assert isinstance(s, float)
    assert 0.0 <= s <= 1.0


def test_train_translate_smoke(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()

    import train_translate
    result = train_translate.main(smoke_test=True)
    assert result is not None
    assert "final_loss" in result
    assert "score" in result
    assert result["final_loss"] >= 0.0
    assert isinstance(result["score"], float)
