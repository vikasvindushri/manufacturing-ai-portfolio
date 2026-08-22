# Advanced Manufacturing AI Portfolio

Three runnable, practical AI transformation projects for Manufacturing, Quality, and Operations. The repository uses synthetic data and local, explainable methods so it can run without paid APIs.

## Projects
1. **AI Quality & 8D Assistant** - extracts incident facts, drafts an 8D, proposes 5-Why paths and corrective actions, and requires human approval.
2. **Manufacturing Knowledge Assistant (RAG)** - indexes local engineering/quality documents with TF-IDF and returns evidence-backed answers with references.
3. **Low-Code Manufacturing AI Agent** - classifies manufacturing faults, recommends checks, and creates a structured action record suitable for Power Apps/AppSheet.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run project_1_quality_8d/app.py
```
Run the other apps by replacing the path with `project_2_rag/app.py` or `project_3_low_code_agent/app.py`.

## CLI examples
```bash
python -m project_1_quality_8d.cli --incident project_1_quality_8d/data/sample_incident.json
python -m project_2_rag.cli --query "What should be checked after a torque failure?"
python -m project_3_low_code_agent.cli --input project_3_low_code_agent/data/sample_fault.json
```

## Portfolio capabilities
Generative-AI solution framing, 8D/RCA/PFMEA thinking, structured extraction, retrieval-augmented generation concepts, human-in-the-loop governance, low-code design, Python, pandas, testing, CI, ROI and adoption planning.

## Safety and scope
This is a portfolio demonstrator, not a production quality-management system. Recommendations are hypotheses. A qualified engineer must validate containment, root cause, product disposition and corrective actions.

## Repository map
- `docs/` stakeholder documentation, architecture, governance, security and demo guide
- `project_1_quality_8d/` quality incident and 8D assistant
- `project_2_rag/` local knowledge retrieval assistant
- `project_3_low_code_agent/` fault triage workflow and connector examples
- `tests/` automated tests
- `.github/workflows/ci.yml` CI pipeline

## License
MIT. Synthetic examples only.
