"""
Check available Gemini models
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(dotenv_path=Path("backend/.env"))

# Configure Gemini
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"API Key (first 10 chars): {gemini_key[:10]}...")

genai.configure(api_key=gemini_key)

print("\n🔍 Available Gemini models:")
models = genai.list_models()
for model in models:
    print(f"- {model.name}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"  Methods: {model.supported_generation_methods}")
    print()