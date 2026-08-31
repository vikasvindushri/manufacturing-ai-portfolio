from pathlib import Path

from shared.version import (
    PHASE_STATUS,
    STABLE_RELEASE,
    WORKFLOW_DEFINITION_VERSION,
    __version__,
)

ROOT = Path(__file__).resolve().parents[1]
CURRENT_DEVELOPMENT_VERSION = "0.7.0-dev.2"


def read_utf8(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_versions_align():
    assert read_utf8("VERSION").strip() == __version__ == CURRENT_DEVELOPMENT_VERSION
    assert STABLE_RELEASE == "0.6"
    assert WORKFLOW_DEFINITION_VERSION == "1.1"
    assert "Increment 2.2" in PHASE_STATUS


def test_docs_align():
    for relative_path in (
        "README.md",
        "CHANGELOG.md",
        "docs/PRODUCT_ROADMAP.md",
        "docs/PHASE_2_INCREMENT_2_2.md",
    ):
        assert f"v{CURRENT_DEVELOPMENT_VERSION}" in read_utf8(relative_path)
