# Security and Data Handling
Do not upload confidential drawings, PII, supplier data or production records to unapproved services. Use secrets management, role-based access, encryption, audit logs, dependency scanning and retention policies. Treat retrieved text as untrusted input and protect against prompt injection when an LLM is added.


## Phase 2 workflow-configuration boundary

- Workflow definitions and prompts must not contain credentials, API keys, tokens, passwords, private keys, or connection strings.
- Unknown definition properties are rejected.
- Confidential or restricted classifications cannot invoke external AI.
- Optional AI must preserve the local-result fallback and human approval.
- Committed preview cases must use synthetic data.
- Definitions are size-limited and cross-references are validated.
- Secure package import, traversal protection, and checksum enforcement are planned for the import/export increment.
