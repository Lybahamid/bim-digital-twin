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

File formats: poses and statuses as JSON/JSONL, point clouds as PLY, meshes as OBJ/IFC, alerts as JSONL.
