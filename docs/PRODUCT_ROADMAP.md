# Product Roadmap

## Product vision

Evolve Manufacturing AI Studio from three demonstration applications into a governed workflow environment in which business users can configure, run, review, and improve manufacturing AI workflows through guided interfaces rather than source-code changes.

## Phase 1 — Product foundation ✅ COMPLETE

**Goal:** Make the current suite reliable and easy to operate.

- [x] Consolidate all products into a single navigation experience.
- [x] Replace raw JSON entry with validated forms; advanced JSON remains available only in individual technical utilities.
- [x] Add editable review screens before export.
- [x] Add session history, draft saving, and reusable sample scenarios.
- [x] Add friendly error states and recovery guidance.
- [x] Add accessibility checks, usage telemetry, and structured audit events.
- [x] Package configuration using environment profiles.

**Exit criteria:** ✅ Met — A first-time user can complete each workflow without reading source code.

**Evidence:** See [`PHASE_1_COMPLETION.md`](PHASE_1_COMPLETION.md).

## Phase 2 — Guided workflow configuration

**Goal:** Allow authorized users to configure common workflows using point-and-click controls.

- Form builder for incident, document-search, and fault-intake fields.
- Rule builder for categories, severity, routing, and approval requirements.
- Prompt-template editor with versioning and approval status.
- Output-schema designer based on supported field types.
- Preview mode with synthetic test cases.
- Template catalog for 8D, nonconformance, equipment fault, layered audit, and knowledge search.
- Configuration import/export using versioned JSON packages.

**Exit criteria:** An authorized user can create a new workflow from a template without editing Python.

## Phase 3 — Data and connector studio

**Goal:** Connect approved information sources and business systems safely.

- Guided document ingestion with metadata, revision, owner, and approval fields.
- Connectors for approved file repositories and structured data sources.
- Managed mapping between application fields and QMS, CMMS, MES, or workflow records.
- Credential storage outside application code.
- Synchronization status, retry queues, and connector health checks.
- Data-classification warnings and configurable retention.
- Read-only sandbox mode before write-back is enabled.

**Exit criteria:** Administrators can configure and validate an approved connector through the user interface.

## Phase 4 — Governance and evaluation center

**Goal:** Make quality, risk, and change control visible.

- Role-based access for creator, reviewer, approver, administrator, and auditor.
- Workflow, prompt, model, rule, and schema version history.
- Evaluation-set manager with expected outputs and reviewer annotations.
- Dashboards for citation coverage, unsupported claims, overrides, failures, and latency.
- Approval workflow for publishing configuration changes.
- Rollback to a prior approved version.
- Policy checks for prohibited data and unsafe instructions.

**Exit criteria:** Every production output can be traced to approved configuration, evidence, model, rules, and human review.

## Phase 5 — Visual workflow studio

**Goal:** Support reusable multi-step manufacturing workflows.

- Drag-and-drop nodes for input, validation, retrieval, rules, Gemini, human review, notification, and export.
- Conditional routing and exception paths.
- Reusable subflows and organization-managed templates.
- Test-run visualization with input/output inspection at every step.
- Publish, clone, archive, and rollback lifecycle.
- Separation between development, test, and production workspaces.

**Exit criteria:** Authorized users can assemble and test a governed workflow visually.

## Phase 6 — Enterprise productization

**Goal:** Operate securely and reliably at scale.

- Enterprise identity and single sign-on.
- Central secrets management and encrypted storage.
- API gateway, rate limits, observability, and service-level objectives.
- Relational storage for cases, approvals, evidence, and configuration.
- Background job processing for document ingestion and evaluations.
- Deployment automation, dependency scanning, backup, and disaster recovery.
- Multi-site configuration with controlled local variation.
- Support model, ownership matrix, release process, and user training.

**Exit criteria:** The product meets the organization's architecture, security, validation, support, and operational-readiness standards.

## Prioritization principles

1. Improve usability before increasing model complexity.
2. Keep local and deterministic fallbacks for critical paths.
3. Require traceability before enabling write-back integrations.
4. Validate with representative users and measured baselines.
5. Introduce new connectors in read-only mode first.
6. Treat prompts, models, rules, schemas, and knowledge sources as controlled configuration.
7. Measure usefulness, risk, and adoption together.
