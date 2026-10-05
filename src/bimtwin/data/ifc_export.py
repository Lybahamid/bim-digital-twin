"""Export selected IFC elements to mesh files for Blender (IFC -> data file step).

Outputs (units metres, Z-up, no rotation needed for Blender):
  elements.npz   arrays ``<guid>__v`` (N,3 float64) and ``<guid>__f`` (M,3 int32)
  elements.json  list of {guid, ifc_class, name, storey, elevation_m, bbox_min, bbox_max, height_m}
"""

import argparse
import json
from pathlib import Path

import numpy as np

from bimtwin.common.config import load_config


def _mesh_from_shape(shape):
    verts = np.array(shape.verts, dtype=float).reshape(-1, 3)
    faces = np.array(shape.faces, dtype=np.int32).reshape(-1, 3)
    return verts, faces


def load_element_mesh(model, element, unit_scale):
    """Return (verts, faces) in metres in world coordinates, or None if no geometry.

    Tries the whole element first (openings applied). Revit walls carry a 2D 'Axis' curve next to
    the 'Body' solid and fail there, so fall back to the Body representation placed with the
    element's placement matrix (openings are not cut).
    """
    from ifcopenshell import geom
    from ifcopenshell.util import placement

    try:
        settings = geom.settings()
        settings.set("use-world-coords", True)
        return _mesh_from_shape(geom.create_shape(settings, element).geometry)
    except RuntimeError:
        pass
    if not element.Representation:
        return None
    bodies = [r for r in element.Representation.Representations
              if r.RepresentationIdentifier == "Body"]
    if not bodies:
        return None
    try:
        verts, faces = _mesh_from_shape(geom.create_shape(geom.settings(), bodies[0]))
    except RuntimeError:
        return None
    m = np.array(placement.get_local_placement(element.ObjectPlacement), dtype=float)
    m[:3, 3] *= unit_scale  # placement is in project units, the mesh is already in metres
    return verts @ m[:3, :3].T + m[:3, 3], faces


def _storey(model, element):
    import ifcopenshell.util.element as el

    container = el.get_container(element)
    if container is not None and container.is_a("IfcBuildingStorey"):
        return container.Name, float(container.Elevation or 0.0)
    return None, None


def collect_records(model, classes):
    """Mesh + metadata for every element of the given IFC classes that has geometry."""
    from ifcopenshell.util import unit

    scale = unit.calculate_unit_scale(model)
    records = []
    for cls in classes:
        for element in model.by_type(cls):
            mesh = load_element_mesh(model, element, scale)
            if mesh is None or len(mesh[1]) == 0:
                continue
            verts, faces = mesh
            storey, elev = _storey(model, element)
            lo, hi = verts.min(0), verts.max(0)
            records.append({
                "guid": element.GlobalId,
                "ifc_class": cls,
                "name": element.Name,
                "storey": storey,
                "elevation_m": None if elev is None else elev * scale,
                "bbox_min": lo.round(4).tolist(),
                "bbox_max": hi.round(4).tolist(),
                "height_m": float(hi[2] - lo[2]),
                "_verts": verts,
                "_faces": faces,
            })
    return records


def _footprint(rec):
    d = np.array(rec["bbox_max"]) - np.array(rec["bbox_min"])
    return float(d[0] * d[1])


def _size(rec):
    d = np.array(rec["bbox_max"]) - np.array(rec["bbox_min"])
    return float(max(d[0], d[1]) * d[2]) if rec["ifc_class"] == "IfcWall" else _footprint(rec) + d[2]


def select_elements(records, rules):
    """Apply selection rules from configs/data.yaml; largest first within each rule."""
    chosen, seen = [], set()
    for rule in rules:
        pool = [r for r in records if r["ifc_class"] == rule["ifc_class"]
                and (rule.get("storeys") is None or r["storey"] in rule["storeys"])
                and _footprint(r) >= rule.get("min_area_m2", 0.0)
                and r["height_m"] <= rule.get("max_height_m", float("inf"))
                and r["guid"] not in seen]
        pool.sort(key=_size, reverse=True)
        for r in pool[: rule.get("max", len(pool))]:
            chosen.append(r)
            seen.add(r["guid"])
    return chosen


def write_export(records, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    arrays, meta = {}, []
    for r in records:
        arrays[f"{r['guid']}__v"] = r["_verts"]
        arrays[f"{r['guid']}__f"] = r["_faces"]
        meta.append({k: v for k, v in r.items() if not k.startswith("_")})
    np.savez_compressed(out / "elements.npz", **arrays)
    (out / "elements.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def export(ifc_path, out_dir, rules):
    import ifcopenshell

    model = ifcopenshell.open(str(ifc_path))
    classes = sorted({r["ifc_class"] for r in rules})  # by_type includes subtypes
    records = collect_records(model, classes)
    return write_export(select_elements(records, rules), out_dir)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Export selected IFC elements for Blender")
    p.add_argument("--config", default="configs/data.yaml")
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    meta = export(cfg["paths"]["ifc"], cfg["paths"]["bim_out"], cfg["selection"])
    print(f"{len(meta)} elements -> {cfg['paths']['bim_out']}")
    for m in meta:
        d = np.array(m["bbox_max"]) - np.array(m["bbox_min"])
        print(f"{m['guid']}  {m['ifc_class']:<9} {m['storey']!s:<12} "
              f"size {d[0]:.2f} x {d[1]:.2f} x {d[2]:.2f} m  {m['name'][:40]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
