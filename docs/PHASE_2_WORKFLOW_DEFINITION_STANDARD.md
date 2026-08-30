# Phase 2 Workflow Definition Standard

## Purpose

The Workflow Definition Standard is the controlled configuration contract for Phase 2 of Manufacturing AI Studio. It allows workflows to be represented as versioned JSON rather than hard-coded user interfaces.

## Initial scope

Version 1.0 defines workflow metadata, input fields, deterministic rules, mandatory human approval, and an extension area. Visual builders, prompt lifecycle, output schema design, and package publishing will build on this contract in later increments.

## Security and governance

- Definitions are strict and reject unknown properties.
- Definitions cannot contain API keys, passwords, tokens, or private keys.
- Human approval cannot be disabled for governed workflows.
- Definitions are limited to 1 MB.
- Gemini remains optional and credentials remain outside workflow packages.
- Only synthetic or approved data belongs in committed templates and tests.

## Validation

```bash
python scripts/export_phase2_schema.py
python -m pytest -q
```

The generated JSON Schema is committed so non-Python clients can validate packages against the same contract.
