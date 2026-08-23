from pathlib import Path
import os,sys
from dotenv import load_dotenv
root=Path(__file__).resolve().parents[1]
loaded=load_dotenv(root/'.env',override=True)
checks={
 "Python >= 3.11":sys.version_info >= (3,11),
 "Repository root":(root/'app.py').exists(),
 ".env loaded":loaded,
 "Gemini enabled":os.getenv('ENABLE_GEMINI','false').lower()=='true',
 "Gemini key present":bool(os.getenv('GEMINI_API_KEY')),
 "Model configured":bool(os.getenv('GEMINI_MODEL')),
}
print('Manufacturing AI Portfolio - Environment Check')
print('-'*50)
for k,v in checks.items():print(f"{'PASS' if v else 'INFO'}  {k}: {v}")
print('Model:',os.getenv('GEMINI_MODEL','local mode'))
print('Key value is intentionally not displayed.')
