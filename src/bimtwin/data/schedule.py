"""4D schedule: planned dates, actual (delayed) dates, and per-epoch ground-truth status.

All dates are integer project days (day 0 = project start). Build order per storey is
slabs -> columns -> walls. The renders follow the *actual* schedule; the pipeline is scored
against the *plan*, so some elements must slip or there is nothing to detect.
"""

import argparse
import csv
import json
import random
from pathlib import Path

from bimtwin.common.config import load_config

CLASS_ORDER = {"IfcSlab": 0, "IfcColumn": 1, "IfcWall": 2}


def plan_schedule(elements, durations, stagger_days=2, start_day=0):
    """Return {guid: (planned_start, planned_finish)}.

    Storeys build bottom-up (elements without a storey use their lowest z). Within a storey a
    class group starts after the previous group finishes; elements in a group are staggered.
    """
    def key(e):
        elev = e.get("elevation_m")
        return (elev if elev is not None else e["bbox_min"][2], CLASS_ORDER.get(e["ifc_class"], 9))

    groups = {}
    for e in sorted(elements, key=key):
        groups.setdefault(key(e), []).append(e)

    plan, cursor = {}, start_day
    for _, members in sorted(groups.items()):
        group_end = cursor
        for i, e in enumerate(members):
            start = cursor + i * stagger_days
            finish = start + durations[e["ifc_class"]]
            plan[e["guid"]] = (start, finish)
            group_end = max(group_end, finish)
        cursor = group_end + 1
    return plan


def actual_schedule(plan, n_delayed=4, start_delay=(2, 5), extra_finish_delay=(3, 6), seed=0):
    """Return {guid: (actual_start, actual_finish)}; ``n_delayed`` random elements slip."""
    rng = random.Random(seed)
    guids = sorted(plan)
    delayed = set(rng.sample(guids, min(n_delayed, len(guids))))
    actual = {}
    for g in guids:
        start, finish = plan[g]
        if g in delayed:
            ds = rng.randint(*start_delay)
            start += ds
            finish += ds + rng.randint(*extra_finish_delay)
        actual[g] = (start, finish)
    return actual


def fraction_built(actual_start, actual_finish, day):
    """Built fraction in [0, 1]; scales an element's height (or thickness) from its base."""
    if day <= actual_start:
        return 0.0
    if day >= actual_finish:
        return 1.0
    return (day - actual_start) / (actual_finish - actual_start)


def status_from_fraction(fraction):
    if fraction <= 0.0:
        return "not_started"
    return "done" if fraction >= 1.0 else "in_progress"


def ground_truth(plan, actual, day):
    """Answer-key rows for one epoch day."""
    rows = []
    for g in sorted(plan):
        frac = fraction_built(*actual[g], day)
        status = status_from_fraction(frac)
        planned_finish = plan[g][1]
        overdue = max(0, day - planned_finish) if status != "done" else 0
        delayed = overdue > 0 or (status == "done" and actual[g][1] > planned_finish)
        rows.append({"guid": g, "status": status, "fraction": round(frac, 4),
                     "planned_finish": planned_finish, "overdue_days": overdue,
                     "delayed": int(delayed)})
    return rows


def _write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_schedules(elements, cfg, out_dir):
    s = cfg["schedule"]
    plan = plan_schedule(elements, s["durations"], s["stagger_days"])
    actual = actual_schedule(plan, s["n_delayed"], tuple(s["start_delay_days"]),
                             tuple(s["extra_finish_delay_days"]), cfg["seed"])
    out = Path(out_dir)
    _write_csv(out / "schedule_plan.csv", ["guid", "planned_start", "planned_finish"],
               [{"guid": g, "planned_start": a, "planned_finish": b} for g, (a, b) in sorted(plan.items())])
    _write_csv(out / "schedule_actual.csv", ["guid", "actual_start", "actual_finish"],
               [{"guid": g, "actual_start": a, "actual_finish": b} for g, (a, b) in sorted(actual.items())])
    cols = ["guid", "status", "fraction", "planned_finish", "overdue_days", "delayed"]
    for i, day in enumerate(s["epoch_days"], start=1):
        _write_csv(out / f"epoch_{i:02d}" / "gt_status.csv", cols, ground_truth(plan, actual, day))
    return plan, actual


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate plan/actual schedules and per-epoch truth")
    p.add_argument("--config", default="configs/data.yaml")
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    elements = json.loads((Path(cfg["paths"]["bim_out"]) / "elements.json").read_text(encoding="utf-8"))
    plan, actual = write_schedules(elements, cfg, cfg["paths"]["synthetic"])
    names = {e["guid"]: e["name"][:32] for e in elements}
    print(f"{len(plan)} elements, epochs at days {cfg['schedule']['epoch_days']}")
    for g in sorted(plan, key=lambda x: plan[x]):
        mark = "  DELAYED" if actual[g] != plan[g] else ""
        print(f"{g}  plan {plan[g]}  actual {actual[g]}  {names[g]}{mark}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
