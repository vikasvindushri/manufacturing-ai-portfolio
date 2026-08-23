install:
	python -m pip install -r requirements.txt

test:
	python -m pytest

check:
	python scripts/check_environment.py

portfolio:
	python -m streamlit run app.py

quality-app:
	python -m streamlit run project_1_quality_8d/app.py

rag-app:
	python -m streamlit run project_2_rag/app.py

agent-app:
	python -m streamlit run project_3_low_code_agent/app.py
