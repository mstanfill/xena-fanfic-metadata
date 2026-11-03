"""Static checks on notebooks/: they stay in step with the scripts and are
committed without outputs (outputs can hold scraped data or local paths)."""
import ast
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))
SCRIPTS = sorted(p.stem for p in (ROOT / "fanfic_scraper" / "scripts").glob("*.py") if p.stem != "__init__")


def code_cells(path):
    nb = json.loads(path.read_text("utf-8"))
    return nb, ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def test_every_script_has_a_notebook_counterpart():
    assert sorted(p.stem for p in NOTEBOOKS) == SCRIPTS


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_is_committed_without_outputs(path):
    nb, _ = code_cells(path)
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == [] and cell["execution_count"] is None


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_code_compiles_and_uses_the_package(path):
    _, sources = code_cells(path)
    for source in sources:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in {"fetch", "parse", "discover", "scripts"}


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_works_from_the_repo_root(path):
    _, sources = code_cells(path)
    assert "os.chdir(REPO_ROOT)" in sources[0]
    assert any("contact_email=CONTACT_EMAIL" in s for s in sources)
