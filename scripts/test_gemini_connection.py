from pathlib import Path
import os
from dotenv import load_dotenv
from google import genai
root=Path(__file__).resolve().parents[1]
load_dotenv(root/'.env',override=True)
key=os.getenv('GEMINI_API_KEY');model=os.getenv('GEMINI_MODEL','gemini-3.6-flash')
if not key:raise SystemExit('GEMINI_API_KEY is missing. Copy .env.example to .env and add your private key.')
print('Testing model:',model);print('API key present: True')
client=genai.Client(api_key=key)
try:
 r=client.models.generate_content(model=model,contents='Reply with exactly: Gemini API connection is working.')
 print('Response:',r.text);print('SUCCESS: Gemini API request completed.')
finally:client.close()
