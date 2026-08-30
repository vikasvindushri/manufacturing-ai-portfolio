from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase2.models import WorkflowDefinition

TARGET = ROOT / "phase2" / "schemas" / "workflow-definition.schema.json"
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(
    json.dumps(WorkflowDefinition.model_json_schema(), indent=2) + "\n",
    encoding="utf-8",
)
print(TARGET)
