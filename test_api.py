import os
from openai import OpenAI

api_key = "TU_API_KEY_AQUI"
client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hola"}]
    )
    print("✅ API funciona correctamente")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Error: {e}")