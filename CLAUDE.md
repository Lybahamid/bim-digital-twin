# BIM Digital Twin & Progress Monitor
Two-person CV project; see docs/PROJECT_OVERVIEW.md. Run `graphify query` before reading many files.
## Environment
- `mamba activate bimtwin`; Laiba is CPU-only, partner has GPU.
- All code must run on CPU for smoke tests; GPU is opt-in via config.
## Conventions (docs/CONVENTIONS.md)
- Units meters, Z-up, right-handed; poses are 4x4 camera-to-world.
- Never commit data, weights or graphify-out/. Data goes through DVC.
## Workflow
- Branch per task, PR to main, tests must pass (`pytest -q`).
