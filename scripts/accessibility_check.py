from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/"app.py",ROOT/"shared"/"ui.py"]
issues=[]
text="\n".join(p.read_text(encoding="utf-8") for p in files)
checks={"page title":"set_page_config" in text,"visible navigation label":"Navigation" in text,
        "required field indication":"*" in text,"error guidance":"Please correct" in text,
        "button labels":"Download" in text,"contrast theme":(ROOT/".streamlit"/"config.toml").exists()}
for name,ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:issues.append(name)
if issues:raise SystemExit(f"Accessibility source checks failed: {issues}")
print("Accessibility source checks passed. Manual keyboard and screen-reader testing is still required.")
