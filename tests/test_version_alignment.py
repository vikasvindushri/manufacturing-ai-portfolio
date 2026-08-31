from pathlib import Path
from shared.version import __version__, STABLE_RELEASE, WORKFLOW_DEFINITION_VERSION

ROOT=Path(__file__).resolve().parents[1]

def test_version_file_and_shared_version_match():
    assert (ROOT/"VERSION").read_text(encoding="utf-8").strip()==__version__=="0.7.0-dev.1"

def test_release_and_contract_versions_are_explicit():
    assert STABLE_RELEASE=="0.6"
    assert WORKFLOW_DEFINITION_VERSION=="1.1"

def test_primary_documents_show_current_status():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    roadmap=(ROOT/"docs/PRODUCT_ROADMAP.md").read_text(encoding="utf-8")
    assert "v0.7.0-dev.1" in readme
    assert "Phase 2" in readme and "In development" in readme
    assert "Increment 2.1" in roadmap and "IN PROGRESS" in roadmap
