"""Pose helpers following docs/CONVENTIONS.md (4x4 camera-to-world, meters, Z-up)."""

import numpy as np


def is_valid_pose(T, atol: float = 1e-6) -> bool:
    """True if T is a 4x4 rigid transform (proper rotation, bottom row [0 0 0 1])."""
    T = np.asarray(T, dtype=float)
    if T.shape != (4, 4):
        return False
    R = T[:3, :3]
    return (
        np.allclose(R @ R.T, np.eye(3), atol=atol)
        and np.isclose(np.linalg.det(R), 1.0, atol=atol)
        and np.allclose(T[3], [0, 0, 0, 1], atol=atol)
    )


def invert_pose(T) -> np.ndarray:
    """Invert a rigid transform (e.g. COLMAP world-to-camera -> camera-to-world)."""
    T = np.asarray(T, dtype=float)
    R, t = T[:3, :3], T[:3, 3]
    out = np.eye(4)
    out[:3, :3] = R.T
    out[:3, 3] = -R.T @ t
    return out


def pose_error(T_a, T_b) -> tuple[float, float]:
    """Return (translation error in meters, rotation error in degrees) between two poses."""
    T_a, T_b = np.asarray(T_a, dtype=float), np.asarray(T_b, dtype=float)
    dt = float(np.linalg.norm(T_a[:3, 3] - T_b[:3, 3]))
    R = T_a[:3, :3].T @ T_b[:3, :3]
    cos = np.clip((np.trace(R) - 1) / 2, -1.0, 1.0)
    return dt, float(np.degrees(np.arccos(cos)))
