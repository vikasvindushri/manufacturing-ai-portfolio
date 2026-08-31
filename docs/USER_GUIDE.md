# User Guide

## Quality Assistant
1. Select the supplied example or paste valid incident JSON.
2. Review input for accuracy and remove sensitive data.
3. Generate the draft.
4. Review missing evidence, hypotheses and proposed actions.
5. If Gemini is enabled, compare its review with the local result.
6. Obtain evidence and edit externally as needed.
7. Enter the qualified approver only after review.
8. Export the case record.

## Knowledge Assistant
1. Ask a focused manufacturing question.
2. Review the answer and every evidence expander.
3. Confirm the source is applicable and current.
4. Treat no-evidence results as an escalation—not permission to improvise.

## Fault Triage Agent
1. Paste a fault event or use the sample.
2. Generate the triage record.
3. Review category, priority, likely causes and checks.
4. Follow approved safety and lockout/tagout procedures.
5. Accept, modify or reject with a rationale.
6. Export the JSON for a downstream workflow.

## Troubleshooting
- Run all commands from repository root.
- Git Bash: `export PYTHONPATH="$PWD"` before launching individual apps.
- Missing packages: `python -m pip install -r requirements.txt`.
- Gemini 404: change `GEMINI_MODEL` to a model available to your key.
- Gemini disabled: verify `.env`, then stop and restart Streamlit.


## Conversational Knowledge Assistant v0.5

1. Add PDF, DOCX, Markdown, TXT, or CSV documents in **Add documents**.
2. Record document number, revision, status, owner, plant, process, and confidentiality.
3. Keep **Released documents only** selected for controlled use.
4. Ask a question in the chat and continue with follow-up questions.
5. Inspect evidence status, [S1] citations, source metadata, and retrieval diagnostics.
6. Gemini semantic search and synthesis are optional. Local hybrid retrieval remains available.


## Phase 2 developer preview - v0.7.0-dev.1

Increment 2.1 is a configuration-contract release. The existing Phase 1 application remains unchanged except for development-version and status indicators. The point-and-click Workflow Studio is not yet available.

Validate the current workflow definition with:

```bash
python scripts/export_phase2_schema.py
python -m pytest -q
```

The next increment adds the five-template catalog and registry, which will become the first visible Phase 2 experience.
