"""GPU training infra smoke test. NOT part of the real training pipeline.

Runs a short YOLO11n training run on the public COCO128 sample to prove the
training stack (dataloader, AMP, checkpointing, throughput) works on this
machine's GPU, and logs the run to Weights & Biases in offline mode. Uses a
public dataset precisely so it needs nothing from DVC or Laiba's Blender
renders. Run with: `python scripts/gpu_smoke_test.py`.
"""

import os
import time

os.environ.setdefault("WANDB_MODE", "offline")

import torch
import wandb
from ultralytics import YOLO

EPOCHS = 3
IMGSZ = 640
BATCH = 16


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA not available in this environment")
    device_name = torch.cuda.get_device_name(0)

    wandb.init(
        project="bimtwin-gpu-smoke-test",
        config={
            "model": "yolo11n.pt",
            "dataset": "coco128.yaml",
            "epochs": EPOCHS,
            "imgsz": IMGSZ,
            "batch": BATCH,
            "device": device_name,
        },
    )

    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()

    model = YOLO("yolo11n.pt")
    results = model.train(
        data="coco128.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=0,
        project="runs/smoke_test",
        name="coco128_yolo11n",
        exist_ok=True,
    )

    elapsed_s = time.perf_counter() - t0
    peak_vram_gb = torch.cuda.max_memory_allocated() / 1e9
    best_ckpt = results.save_dir / "weights" / "best.pt"

    summary = {
        "device": device_name,
        "wall_time_s": round(elapsed_s, 1),
        "s_per_epoch": round(elapsed_s / EPOCHS, 1),
        "peak_vram_gb": round(peak_vram_gb, 2),
        "checkpoint_saved": best_ckpt.exists(),
        "checkpoint_path": str(best_ckpt),
    }
    print("\n=== GPU smoke test summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    wandb.log({k: v for k, v in summary.items() if isinstance(v, (int, float))})
    wandb.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
