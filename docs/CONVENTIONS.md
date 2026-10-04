# Conventions

## Geometry
- Units: **meters** everywhere (convert IFC/Blender units on import).
- World frame: **Z-up, right-handed**, origin at the BIM project origin.
- Poses are **4x4 camera-to-world** matrices (`T_wc`). Camera axes: OpenCV style (x right, y down, z forward). COLMAP world-to-camera output must be inverted on import.
- Rotation error in degrees, translation error in meters.

## Code
- Python >= 3.10, src layout, package `bimtwin`. Lint with `ruff`, test with `pytest -q`.
- All code must run on CPU for smoke tests. GPU is opt-in via `device: cuda` in config.
- Configs are YAML in `configs/`; no hard-coded paths.

## Repo
- Never commit data, weights or `graphify-out/`. Data goes through DVC.
- Branch per task, PR to `main`, tests must pass.
- Dates in schedules and logs use ISO 8601 (`YYYY-MM-DD`).
