import numpy as np

from bimtwin.common.transforms import invert_pose, is_valid_pose, pose_error


def _pose(yaw_deg=30.0, t=(1.0, 2.0, 3.0)):
    a = np.radians(yaw_deg)
    T = np.eye(4)
    T[:3, :3] = [[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]
    T[:3, 3] = t
    return T


def test_valid_and_invalid():
    assert is_valid_pose(_pose())
    bad = _pose()
    bad[:3, :3] *= 2
    assert not is_valid_pose(bad)
    assert not is_valid_pose(np.eye(3))


def test_invert_roundtrip():
    T = _pose()
    assert np.allclose(T @ invert_pose(T), np.eye(4))


def test_pose_error():
    dt, dr = pose_error(_pose(0), _pose(10, t=(1.0, 2.0, 3.5)))
    assert np.isclose(dt, 0.5)
    assert np.isclose(dr, 10.0)
