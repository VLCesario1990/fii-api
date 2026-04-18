import google.generativeai as genai

genai.configure(api_key="AIzaSyAj1w4yrtT_1210T5ZUT7kaF6xZ-xCtqUI")

model = genai.GenerativeModel("gemini-pro")

prompt = """
Inadimplência XPML11
"""

response = model.generate_content(prompt)
print(response.text)
