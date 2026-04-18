import os
from google import genai

fii = "XPML11"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"""
Analise o fundo {fii}:

- Inadimplência
- Vacância

Explique situação atual e riscos.
"""
)

print(response.text)
