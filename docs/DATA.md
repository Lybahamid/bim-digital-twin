# Data

Nothing under `data/` is committed. Large files go through DVC. Sources and licences are tracked in [ASSETS.md](ASSETS.md).

## Layout
```
data/raw/ifc/wellness_center.ifc        source BIM (IFC2X3, Revit export)
data/raw/ppe/                           public PPE dataset (YOLO format, 4 classes)
data/raw/assets/                        downloaded 3D assets (characters, ppe_models, props, hdri)
data/processed/bim/                     elements.npz + elements.json   (from ifc_export)
data/processed/ppe/                     cleaned PPE dataset with train/valid/test (from ppe)
data/synthetic/                         schedule_plan.csv, schedule_actual.csv, epoch_NN/ (Blender output)
```

## Commands (run inside `mamba activate bimtwin`, from the repo root; settings in `configs/data.yaml`)
```
python -m bimtwin.data.ifc_export   # 12 selected elements -> data/processed/bim/
python -m bimtwin.data.schedule     # plan, actual, per-epoch gt_status.csv -> data/synthetic/
python -m bimtwin.data.ppe          # data/processed/ppe/ + stats.json
```

## BIM export
- Elements are chosen by rules in `configs/data.yaml`: 2 slabs (ground, first floor), 3 columns, 7 single-storey walls (about 12 elements).
- Geometry is in metres, Z-up, world coordinates. IfcOpenShell already converts the IFC's millimetres.
- Revit walls fail as whole elements (a 2D axis curve sits next to the solid), so walls use the Body representation plus the placement matrix. Door and window openings are therefore not cut in walls.
- Storey name in the IFC is spelled `Grond floor`; the config uses that spelling.

## Schedule
- Dates are integer project days (day 0 = project start). Build order per storey: slabs, then columns, then walls.
- `schedule_plan.csv`: guid, planned_start, planned_finish. `schedule_actual.csv`: guid, actual_start, actual_finish. Four elements slip (seeded, `seed` in config).
- `gt_status.csv` per epoch (days 10, 20, ... 60): guid, status (`not_started`/`in_progress`/`done`), fraction, planned_finish, overdue_days, delayed.
- Fraction = (day - actual_start) / (actual_finish - actual_start), clipped to [0, 1]. Example: actual 24-40 on day 35 gives 0.6875.
- Delays do not yet propagate to later elements (a late slab does not push back its walls). Add later if wanted.

## PPE dataset
- 2169 images, 4 classes: `Helmet`, `NoHelmet`, `NoVest`, `Vest`. There is no `person` class, so the tracker uses a COCO-pretrained person detector and this dataset supplies the PPE classes.
- Original split was train 1736 / valid 433 / test empty. `ppe.py` splits valid in half with a fixed seed: train 1736, valid 217, test 216. Files are hardlinked, not copied.
- Class counts are imbalanced (train: Helmet 1936, Vest 1039, NoHelmet 860, NoVest 774). Report per-class AP, not only mAP.

## Windows note
Run Python from an activated environment (`mamba activate bimtwin`). Calling the env's `python.exe` directly leaves conda's `Library\bin` off PATH and numpy matrix maths crashes with exit code 0xc06d007f.
