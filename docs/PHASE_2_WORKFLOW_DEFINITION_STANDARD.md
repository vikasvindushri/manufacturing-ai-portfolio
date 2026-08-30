# Phase 2 Workflow Definition Standard

**Product:** Manufacturing AI Studio  
**Increment:** Phase 2.1  
**Definition contract:** 1.1

The standard is the controlled contract for future point-and-click builders. It covers metadata, intake fields, validation, rules, routing, governed prompt references, output schemas, data classification, optional AI with local fallback, mandatory human approval, and synthetic preview cases.

Security controls reject unknown properties, nested secret-bearing properties, confidential external-AI use, invalid cross-references, and definitions larger than 1 MB. Definition versions 1.0 and 1.1 are supported.

```bash
python scripts/export_phase2_schema.py
python -m pytest -q
```
