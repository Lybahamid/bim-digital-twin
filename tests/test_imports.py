import importlib

import pytest


@pytest.mark.parametrize("sub", ["common", "data", "recon", "safety", "edge", "pipeline"])
def test_subpackages_import(sub):
    importlib.import_module(f"bimtwin.{sub}")


def test_cli_runs():
    from bimtwin.pipeline.cli import main

    assert main([]) == 0
