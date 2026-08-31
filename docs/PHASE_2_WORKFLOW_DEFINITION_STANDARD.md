# Phase 2 Workflow Definition Standard

**Introduced in development build:** v0.7.0-dev.1
**Stable product baseline:** v0.6
**Definition Contract:** 1.1

This controlled contract supports workflow metadata, input fields, validation constraints, deterministic rules, routing actions, governed prompt references, output schemas, data-classification and optional-AI policy, mandatory human approval, and synthetic preview cases.

Definitions reject unknown properties, secret-bearing properties, invalid cross-references, confidential external-AI use, missing local fallback, disabled approval, and unsupported contract versions.

```bash
python scripts/export_phase2_schema.py
python -m pytest -q
```
