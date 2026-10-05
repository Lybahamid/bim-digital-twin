from bimtwin.data.ifc_export import select_elements


def _rec(guid, cls, storey, size, height=3.0):
    return {"guid": guid, "ifc_class": cls, "storey": storey,
            "bbox_min": [0.0, 0.0, 0.0], "bbox_max": [size[0], size[1], height],
            "height_m": height}


def test_select_ranks_filters_and_caps():
    recs = [_rec("s_big", "IfcSlab", "A", (30, 30)), _rec("s_small", "IfcSlab", "A", (2, 2)),
            _rec("w1", "IfcWall", "A", (10, 0.2)), _rec("w2", "IfcWall", "A", (4, 0.2)),
            _rec("w_core", "IfcWall", "A", (10, 0.2), height=12.0),
            _rec("w_other", "IfcWall", "Z", (20, 0.2))]
    rules = [{"ifc_class": "IfcSlab", "storeys": ["A"], "min_area_m2": 20, "max": 2},
             {"ifc_class": "IfcWall", "storeys": ["A"], "max_height_m": 5.0, "max": 1}]
    assert [r["guid"] for r in select_elements(recs, rules)] == ["s_big", "w1"]
