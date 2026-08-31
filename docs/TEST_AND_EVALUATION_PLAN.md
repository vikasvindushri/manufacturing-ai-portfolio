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


## Phase 2.1 validation scope

The v0.7.0-dev.1 development build adds tests for workflow models, field constraints, cross-reference validation, definition-version compatibility, nested-secret rejection, data-classification restrictions, mandatory local fallback, mandatory approval, and synthetic test-case enforcement.

**Current automated validation target:** 61 tests passing with no failures.
