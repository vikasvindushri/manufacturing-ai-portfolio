# Release History

## v0.7.0-dev.2 - Phase 2.2 Template Catalog and Registry

**Status:** Development prerelease
**Stable baseline:** v0.6
**Workflow Definition Contract:** 1.1

### Added
- Visible Workflow Studio Template Catalog
- Five governed starter workflow templates
- Search, domain filtering, validation metadata, governance summary, and JSON preview
- Safe clone-as-draft preview and JSON download
- Registry discovery, unique-ID checks, and controlled lifecycle transitions

### Safety
- Catalog actions do not write operational records or repository files
- Templates require human approval and synthetic committed test cases
- AI-enabled templates require local fallback and exclude confidential external-AI use

---

## v0.6 — Shared Truck-X Manufacturing Knowledge Hub

**Release date:** August 27, 2026  
**Release status:** Current  
**Release type:** Shared knowledge platform

### Added
- Shared synthetic Truck-X knowledge catalog with more than 50 released topics
- Domains for quality, manufacturing process, maintenance, safety, regulatory, engineering, digital manufacturing, and supply chain
- Day-cab and sleeper-truck applicability
- Common metadata, authority class, workflow applicability, public reference starting points, and revision status
- Shared retrieval integration with Quality & 8D, Knowledge Assistant, and Fault Triage
- Knowledge Hub catalog page and cross-workflow references in exported records

### Safety and legal boundary
The library summarizes public concepts and synthetic Truck-X assumptions. It is not a substitute for current regulations, licensed standards, approved drawings, or site procedures.

---

## v0.5 — Conversational Manufacturing Knowledge Assistant

**Release date:** August 27, 2026  
**Release status:** Current  
**Release type:** Knowledge retrieval and conversational experience

### Added
- Local PDF, DOCX, Markdown, TXT, and CSV upload
- Document metadata and released-document filtering
- Heading-aware overlapping chunks
- Hybrid word, character, exact-term, and optional semantic retrieval
- Optional Gemini embeddings and grounded conversational synthesis
- Metadata filters, evidence-sufficiency gate, structured answers, citations, local fallback, and follow-up questions
- Knowledge-base status, retrieval diagnostics, feedback capture, and frozen evaluation set
- Recall@3 and no-evidence evaluation

### Reliability
The assistant remains fully usable without Gemini. Local hybrid retrieval and extractive conversational answers remain available when Gemini is disabled or unavailable.

---

This document is the source of truth for released product changes beginning with version 0.2.

The repository README describes the current product. The [Product Roadmap](docs/PRODUCT_ROADMAP.md) describes planned capabilities, and the [Phase 1 Completion Report](docs/PHASE_1_COMPLETION.md) records the evidence used to mark Phase 1 complete.

## v0.4 — Phase 1 Product Hardening

**Release date:** August 23, 2026  
**Release status:** Current  
**Phase:** Phase 1 — Product Foundation  
**Release type:** Product hardening, governance, and usability

### Summary

Version 0.4 completes the Phase 1 product-hardening scope. It improves report presentation, transparency, review controls, data classification, optional AI selection, readiness visibility, and operational diagnostics while retaining resilient local execution.

### Added

- Professional report headers with record, status, owner, analysis source, and release version
- Record-readiness indicators for quality investigations and fault intake
- Separate views for verified inputs, evidence gaps, hypotheses, and recommendations
- Side-by-side comparison of local analysis and optional Gemini review
- Retry of optional Gemini enhancement without regenerating or discarding local work
- Per-case data classification
- Per-case selection of optional Gemini enhancement
- Automatic local-only behavior for confidential or restricted classifications
- Expanded human-review decisions: accept, accept with modifications, return for information, reject, and escalate
- Reviewer name, reviewer role, rationale, evidence review, and required follow-up fields
- System Health page for core engines, knowledge base, Gemini configuration, audit state, and profile visibility
- Improved print-ready HTML styling
- Product-hardening tests for readiness and system health

### Changed

- Result presentation now emphasizes manufacturing records rather than raw AI output
- Local and Gemini contributions are displayed separately
- Readiness is explicitly presented as record completeness, not correctness or confidence
- Phase 1 completion evidence and roadmap status were updated to version 0.4

### Reliability and Governance

- Core local workflows remain available when Gemini is disabled or unavailable
- Confidential or restricted cases cannot request Gemini enhancement from the user interface
- Retry actions produce structured audit events
- Human validation remains required for all outcomes

### Validation

- 25 automated tests passed
- Python compilation passed
- Accessibility source checks passed
- ZIP integrity verification passed

### Upgrade Notes

- Preserve the private `.env` file when replacing repository contents
- Reinstall dependencies from `requirements.txt`
- Run `python -m pytest` and `python scripts/accessibility_check.py`
- Confirm `VERSION` contains `0.4`

---

## v0.3 — Resilient Local Execution

**Release date:** August 23, 2026  
**Release status:** Superseded by v0.4  
**Phase:** Phase 1 — Product Foundation  
**Release type:** Reliability and fallback

### Summary

Version 0.3 established the local engines as the dependable processing baseline. Gemini became an optional enhancement that cannot prevent a successful local workflow from completing.

### Added

- Resilient workflow service layer under `services/workflows.py`
- Explicit result-source messaging in the interface and readable reports
- Gemini states: `not_requested`, `success`, and `failed`
- Provenance fields for local-engine status, Gemini request status, Gemini use, result source, model, and failure type
- Non-blocking warnings when optional Gemini enhancement is unavailable
- Fallback documentation under `docs/LOCAL_AND_GEMINI_EXECUTION.md`
- Automated outage tests across Quality, Knowledge, and Fault Triage

### Changed

- Local workflow processing and Gemini enrichment now use separate failure boundaries
- Successful local records are stored before any optional AI outcome affects the user experience
- Knowledge search falls back to the local evidence summary when Gemini synthesis fails
- Quality and Fault Triage preserve local outputs when structured Gemini review fails

### Reliability and Governance

- Missing keys, unsupported models, network interruption, timeouts, rate limits, malformed responses, and SDK errors no longer discard successful local outcomes
- The application explicitly states when Gemini was not used
- No-evidence knowledge searches do not ask Gemini to invent an answer

### Validation

- 21 automated tests passed
- Python compilation passed
- ZIP integrity verification passed

### Upgrade Notes

- Use `APP_PROFILE=local` for local-only operation
- Use `APP_PROFILE=gemini` and `ENABLE_GEMINI=true` for optional enrichment
- Invalid-model testing can be used to verify runtime fallback, then the supported model must be restored

---

## v0.2 — Human-Readable Results

**Release date:** August 23, 2026  
**Release status:** Superseded by v0.3  
**Phase:** Phase 1 — Product Foundation  
**Release type:** Usability and reporting

### Summary

Version 0.2 separated business-user documentation from technical integration data. Users gained plain-language reports and editable or printable downloads, while JSON remained available for automation and future system integration.

### Added

- Plain-language documentation view for Quality, Knowledge, and Fault Triage results
- Readable Markdown download
- Printable HTML download
- Human-readable records in Session History
- Version indicator in the application sidebar
- `VERSION` file and `shared/version.py`
- Tests for Quality, Knowledge, Fault, and HTML document generation

### Changed

- JSON is presented as a technical download rather than the only user-facing outcome
- Reports use manufacturing-oriented headings, normal sentences, lists, review status, evidence, and cautions
- The README and completion report describe dual-format business and technical outputs

### Retained

- JSON downloads for APIs, QMS, CMMS, MES, Power Apps, AppSheet, Power Automate, automated testing, and future persistence
- Validated forms, editable review, session drafts, audit events, profiles, local execution, and optional Gemini support

### Validation

- 16 automated tests passed
- Python compilation passed
- ZIP integrity verification passed

### Upgrade Notes

- Users can open printable HTML in a browser and use Print → Save as PDF
- Markdown remains appropriate for editing and documentation workflows
- JSON remains the machine-readable integration contract
