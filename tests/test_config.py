from bimtwin.common.config import load_config


def test_defaults_cpu():
    assert load_config()["device"] == "cpu"


def test_default_yaml_loads(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("paths:\n  data: foo\n", encoding="utf-8")
    cfg = load_config(p)
    assert cfg["paths"] == {"data": "foo", "outputs": "outputs"}
    assert cfg["device"] == "cpu"
