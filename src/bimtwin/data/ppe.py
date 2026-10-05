"""Prepare the public PPE detection dataset (YOLO format) for training.

Checks image/label pairs, creates the missing test split from valid (fixed seed), writes a
portable data.yaml (relative paths) and a stats report. Files are hardlinked where possible.
"""

import argparse
import json
import os
import random
import shutil
from collections import Counter
from pathlib import Path

import yaml

from bimtwin.common.config import load_config

IMG_EXT = {".jpg", ".jpeg", ".png"}


def read_labels(path):
    """Parse a YOLO label file; return (boxes, n_bad). boxes = [(cls, x, y, w, h)]."""
    boxes, bad = [], 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            cls, *vals = parts
            vals = [float(v) for v in vals]
            if len(vals) != 4 or not all(0.0 <= v <= 1.0 for v in vals):
                raise ValueError
            boxes.append((int(cls), *vals))
        except ValueError:
            bad += 1
    return boxes, bad


def find_pairs(split_dir):
    """Return (pairs, orphans): pairs of (image, label) paths, and images without a label file."""
    img_dir, lbl_dir = Path(split_dir) / "images", Path(split_dir) / "labels"
    pairs, orphans = [], []
    for img in sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMG_EXT):
        lbl = lbl_dir / (img.stem + ".txt")
        (pairs if lbl.exists() else orphans).append((img, lbl) if lbl.exists() else img)
    return pairs, orphans


def _place(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def class_stats(pairs, names):
    counts, bad = Counter(), 0
    for _, lbl in pairs:
        boxes, b = read_labels(lbl)
        bad += b
        counts.update(c for c, *_ in boxes)
    return {"boxes": {names[c] if c < len(names) else str(c): n for c, n in sorted(counts.items())},
            "bad_lines": bad}


def prepare(src, dst, test_fraction=0.5, seed=0):
    src, dst = Path(src), Path(dst)
    names = yaml.safe_load((src / "data.yaml").read_text(encoding="utf-8"))["names"]
    train, train_orphans = find_pairs(src / "train")
    valid, valid_orphans = find_pairs(src / "valid")

    rng = random.Random(seed)
    valid = sorted(valid)
    rng.shuffle(valid)
    n_test = int(len(valid) * test_fraction)
    splits = {"train": train, "test": valid[:n_test], "valid": valid[n_test:]}

    for split, pairs in splits.items():
        for img, lbl in pairs:
            _place(img, dst / split / "images" / img.name)
            _place(lbl, dst / split / "labels" / lbl.name)

    (dst / "data.yaml").write_text(yaml.safe_dump(
        {"path": ".", "train": "train/images", "val": "valid/images", "test": "test/images",
         "nc": len(names), "names": names}, sort_keys=False), encoding="utf-8")

    report = {"names": names,
              "orphan_images": len(train_orphans) + len(valid_orphans),
              "splits": {s: {"images": len(p), **class_stats(p, names)} for s, p in splits.items()}}
    (dst / "stats.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Prepare the PPE dataset")
    p.add_argument("--config", default="configs/data.yaml")
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    report = prepare(cfg["paths"]["ppe_raw"], cfg["paths"]["ppe_out"],
                     cfg["ppe"]["test_fraction_of_valid"], cfg["seed"])
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
