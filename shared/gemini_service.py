import json, os
from typing import Type
from pydantic import BaseModel
class GeminiUnavailable(RuntimeError): pass

def enabled(): return os.getenv("ENABLE_GEMINI","false").lower()=="true" and bool(os.getenv("GEMINI_API_KEY"))
def model_name(): return os.getenv("GEMINI_MODEL","gemini-3.6-flash")
def generate_structured(system_prompt:str,user_prompt:str,schema:Type[BaseModel]):
    if not enabled(): raise GeminiUnavailable("Gemini is disabled or GEMINI_API_KEY is missing.")
    from google import genai
    from google.genai import types
    client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    try:
        response=client.models.generate_content(
          model=model_name(), contents=user_prompt,
          config=types.GenerateContentConfig(system_instruction=system_prompt,response_mime_type="application/json",response_schema=schema,temperature=0.2)
        )
        return schema.model_validate_json(response.text).model_dump()
    finally: client.close()
def generate_grounded_answer(question,evidence):
    if not enabled(): raise GeminiUnavailable("Gemini is disabled or GEMINI_API_KEY is missing.")
    from google import genai
    from google.genai import types
    client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt=f"Answer only from EVIDENCE. If insufficient, say so. Cite sources in square brackets.\nQUESTION: {question}\nEVIDENCE:\n{evidence}"
    try:
      r=client.models.generate_content(model=model_name(),contents=prompt,config=types.GenerateContentConfig(temperature=0.1))
      return r.text
    finally: client.close()
