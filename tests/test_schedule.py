import csv

import pytest

from bimtwin.common.config import load_config
from bimtwin.data.schedule import (
    actual_schedule,
    fraction_built,
    ground_truth,
    plan_schedule,
    status_from_fraction,
    write_schedules,
)

DUR = {"IfcSlab": 8, "IfcColumn": 6, "IfcWall": 8}


def _elements():
    def el(guid, cls, elev):
        return {"guid": guid, "ifc_class": cls, "elevation_m": elev, "bbox_min": [0, 0, elev]}

    return [el("w1", "IfcWall", 0.0), el("s1", "IfcSlab", 0.0), el("c1", "IfcColumn", 0.0),
            el("s2", "IfcSlab", 4.0), el("w2", "IfcWall", 4.0)]


def test_worked_example_fraction():
    # doc example: actual 24-40, day 35 -> 11/16
    assert fraction_built(24, 40, 35) == pytest.approx(0.6875)
    assert status_from_fraction(fraction_built(24, 40, 35)) == "in_progress"


def test_fraction_bounds():
    assert fraction_built(5, 10, 5) == 0.0
    assert fraction_built(5, 10, 10) == 1.0
    assert status_from_fraction(0.0) == "not_started"
    assert status_from_fraction(1.0) == "done"


def test_plan_order_slab_column_wall_bottom_up():
    plan = plan_schedule(_elements(), DUR, stagger_days=2)
    assert plan["s1"][1] < plan["c1"][0] < plan["c1"][1] < plan["w1"][0]
    assert plan["w1"][1] < plan["s2"][0]  # next storey starts after the lower one finishes
    assert plan["s2"][1] < plan["w2"][0]


def test_actual_delays_are_seeded_and_only_slip_later():
    plan = plan_schedule(_elements(), DUR)
    a1 = actual_schedule(plan, n_delayed=2, seed=1)
    assert a1 == actual_schedule(plan, n_delayed=2, seed=1)
    changed = [g for g in plan if a1[g] != plan[g]]
    assert len(changed) == 2
    assert all(a1[g][0] > plan[g][0] and a1[g][1] > plan[g][1] for g in changed)


def test_ground_truth_overdue():
    plan = {"w": (21, 30)}
    actual = {"w": (24, 40)}
    row = ground_truth(plan, actual, 35)[0]
    assert row["status"] == "in_progress"
    assert row["fraction"] == pytest.approx(0.6875, abs=1e-4)
    assert row["overdue_days"] == 5 and row["delayed"] == 1


def test_write_schedules(tmp_path):
    cfg = load_config()
    cfg["seed"] = 0
    cfg["schedule"] = {"epoch_days": [5, 30], "durations": DUR, "stagger_days": 2,
                       "n_delayed": 1, "start_delay_days": [2, 3],
                       "extra_finish_delay_days": [3, 4]}
    write_schedules(_elements(), cfg, tmp_path)
    assert (tmp_path / "schedule_plan.csv").exists()
    with open(tmp_path / "epoch_02" / "gt_status.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5 and {"guid", "status", "fraction", "overdue_days"} <= set(rows[0])
