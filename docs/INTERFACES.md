# Interfaces

Contracts between modules. All geometry follows [CONVENTIONS.md](CONVENTIONS.md). Draft for week 1; refine in weeks 2-3.

| Object | Fields | Produced by | Consumed by |
|---|---|---|---|
| `CameraPose` | `image_id`, `T_wc` (4x4, camera-to-world, BIM frame), `K` (3x3), `timestamp` | recon (COLMAP + alignment) | safety (hazard distance) |
| `BIMElement` | `guid`, `ifc_class`, `mesh`/bbox, `planned_start`, `planned_end` | data (IFC + schedule) | recon, pipeline |
| `ElementStatus` | `guid`, `date`, `status` (`not_started`/`in_progress`/`done`), `delayed` (bool), `volume_m3` | recon/pipeline | dashboard, metrics |
| `Detection` | `frame`, `bbox_xyxy`, `cls` (`person`, `helmet`, `vest`, ...), `score` | safety detector | tracker |
| `Track` | `track_id`, `frame`, `bbox_xyxy`, `ppe_ok` (bool) | safety tracker | alert logic |
| `HazardZone` | `id`, `polygon`/box in BIM frame (m), `kind` | data (BIM) | safety |
| `SafetyAlert` | `timestamp`, `track_id`, `hazard_id`, `distance_m`, `reason` | safety | alert log (CSV/JSONL) |
| `AdvisorQuery` *(draft, unsettled)* | TBD -- shape depends on the open "replace vs. augment" question in [VLM_ADVISOR.md](VLM_ADVISOR.md) | user | vlm advisor |
| `AdvisorResponse` *(draft, unsettled)* | TBD -- same | vlm advisor | user |

File formats: poses and statuses as JSON/JSONL, point clouds as PLY, meshes as OBJ/IFC, alerts as JSONL.

## Data files (weeks 2-3)
- `elements.json` records: `guid`, `ifc_class` (IfcSlab/IfcColumn/IfcWall), `name`, `storey`, `elevation_m`, `bbox_min`, `bbox_max`, `height_m`. Meshes in `elements.npz` as `<guid>__v` / `<guid>__f` (metres, world frame).
- `schedule_plan.csv`: `guid, planned_start, planned_finish` (project days). `schedule_actual.csv`: `guid, actual_start, actual_finish`.
- `epoch_NN/gt_status.csv`: `guid, status, fraction, planned_finish, overdue_days, delayed`. `ElementStatus` predictions are scored against it.
- `epoch_NN/cameras.json`: `width, height, K, frames[{id, T_wc}]` with `T_wc` camera-to-world, OpenCV axes. Details in [BLENDER_HANDOFF.md](BLENDER_HANDOFF.md).

