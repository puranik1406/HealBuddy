import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:20]}..." if api_key else "No API key found")

try:
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nAvailable models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Try with gemini-2.5-flash (more widely available)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Test prompt
    response = model.generate_content("Say 'Hello from Gemini!'")
    print(f"\n✅ Gemini API is working!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
