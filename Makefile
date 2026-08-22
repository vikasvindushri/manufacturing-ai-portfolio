install:
	pip install -r requirements.txt

test:
	pytest

quality-app:
	streamlit run project_1_quality_8d/app.py

rag-app:
	streamlit run project_2_rag/app.py

agent-app:
	streamlit run project_3_low_code_agent/app.py
