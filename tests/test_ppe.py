import yaml

from bimtwin.data.ppe import find_pairs, prepare, read_labels


def _make_split(root, split, stems, orphan=None):
    (root / split / "images").mkdir(parents=True)
    (root / split / "labels").mkdir(parents=True)
    for i, stem in enumerate(stems):
        (root / split / "images" / f"{stem}.jpg").write_bytes(b"x")
        (root / split / "labels" / f"{stem}.txt").write_text(f"{i % 2} 0.5 0.5 0.2 0.2\n")
    if orphan:
        (root / split / "images" / f"{orphan}.jpg").write_bytes(b"x")


def _raw(tmp_path):
    raw = tmp_path / "raw"
    _make_split(raw, "train", [f"t{i}" for i in range(4)])
    _make_split(raw, "valid", [f"v{i}" for i in range(4)], orphan="lonely")
    (raw / "data.yaml").write_text("path: C:/abs/path\nnc: 2\nnames: ['Helmet', 'NoHelmet']\n")
    return raw


def test_read_labels_flags_bad_lines(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("1 0.5 0.5 0.2 0.2\n2 0.1 0.2\n0 1.5 0.5 0.2 0.2\n")
    boxes, bad = read_labels(p)
    assert boxes == [(1, 0.5, 0.5, 0.2, 0.2)] and bad == 2


def test_find_pairs_reports_orphans(tmp_path):
    raw = _raw(tmp_path)
    pairs, orphans = find_pairs(raw / "valid")
    assert len(pairs) == 4 and [o.stem for o in orphans] == ["lonely"]


def test_prepare_splits_and_writes_portable_yaml(tmp_path):
    raw = _raw(tmp_path)
    report = prepare(raw, tmp_path / "out", test_fraction=0.5, seed=0)
    assert report["orphan_images"] == 1
    assert [report["splits"][s]["images"] for s in ("train", "valid", "test")] == [4, 2, 2]
    cfg = yaml.safe_load((tmp_path / "out" / "data.yaml").read_text())
    assert cfg["path"] == "." and cfg["test"] == "test/images" and cfg["nc"] == 2
    # no leakage between valid and test
    v = {p.name for p in (tmp_path / "out" / "valid" / "images").iterdir()}
    t = {p.name for p in (tmp_path / "out" / "test" / "images").iterdir()}
    assert not v & t
