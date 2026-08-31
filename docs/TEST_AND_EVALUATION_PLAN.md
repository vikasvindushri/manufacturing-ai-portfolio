# Test and Evaluation Plan

## Software tests
- Input normalization and missing-field behavior.
- Deterministic 8D approval default.
- Retrieval relevance and no-evidence behavior.
- Fault classification and safe fallback.
- Gemini-disabled behavior and schema validation.

## AI evaluations
Create a frozen SME-reviewed set and measure:
- Required-field extraction accuracy.
- Root-cause-hypothesis usefulness; never score unverified hypotheses as facts.
- Retrieval recall@k and citation precision.
- Unsupported-claim rate in generated answers.
- Triage classification agreement.
- Safety-policy violation count.
- Human accept/modify/reject distribution.

## Pilot design
Run in shadow mode, compare with existing decisions, investigate disagreements, and establish go/no-go thresholds before workflow integration.

## Phase 2.2 validation scope

Validate all five templates, unique workflow IDs, catalog search and filtering, lifecycle transitions, clone-as-draft behavior, approval policy, synthetic cases, local fallback, confidential-data restrictions, Workflow Studio rendering boundaries, and version alignment.
