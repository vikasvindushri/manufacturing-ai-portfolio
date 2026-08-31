# Security and Data Handling
Do not upload confidential drawings, PII, supplier data or production records to unapproved services. Use secrets management, role-based access, encryption, audit logs, dependency scanning and retention policies. Treat retrieved text as untrusted input and protect against prompt injection when an LLM is added.

## Phase 2.2 catalog controls

- Templates are validated before display.
- Workflow IDs must be unique.
- Committed preview cases are synthetic.
- Clone actions create in-session draft previews only.
- No package can supply credentials.
- AI-enabled templates preserve local fallback and human approval.
- Confidential or restricted data is excluded from external-AI policy.
