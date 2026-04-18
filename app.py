import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-pro")

prompt = "Inadimplência XPML11"

response = model.generate_content(prompt)
print(response.text)
