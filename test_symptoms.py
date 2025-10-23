import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('models/gemini-2.5-flash')

symptoms_text = "I have a headache"
severity = 5

severity_text = f"Patient-reported severity level: {severity}/10"

prompt = f"""
You are a medical analysis AI. Analyze these patient symptoms and provide a detailed medical assessment.

Symptoms: {symptoms_text}
{severity_text}

First, parse and extract individual symptoms. For each symptom, provide a suggested default severity (1-10) based on the text.

If more information is required to make a confident assessment (for example: onset, associated symptoms, aggravating/alleviating factors, fever, breathing difficulty, etc.), include a list of follow_up_questions the system should ask the patient. Each follow-up question should be a short, focused question.

Respond with this exact JSON structure (fields not applicable can be empty arrays/strings):
{{
    "identified_symptoms": ["symptom1", "symptom2", ...],
    "default_severities": [5, 5, ...],
    "follow_up_questions": ["question 1", "question 2"],
    "duration": "how long symptoms have been present (if mentioned)",
    "urgency": "low/medium/high",
    "possible_conditions": [
        "condition 1 with brief description",
        "condition 2 with brief description"
    ],
    "recommendations": "initial recommendations for home care and when to seek medical attention",
    "diagnosis": "brief preliminary analysis",
    "suggested_medications": [
        {{
            "name": "medication name",
            "purpose": "what it treats",
            "notes": "usage notes/warnings"
        }}
    ],
    "red_flags": ["any concerning symptoms that need immediate attention"]
}}

Rules:
1. Provide concise follow-up questions only when needed.
2. Do NOT provide definitive diagnoses — only preliminary suggestions.
3. Keep medication suggestions limited to common over-the-counter options and include cautions.
4. If any red flags appear, set urgency to "high" and include them in red_flags.
5. Keep the JSON valid and parsable — do not wrap the JSON in markdown fences or code blocks.
6. Return ONLY the JSON structure, no additional text before or after.
"""

try:
    print("Sending request to Gemini AI...")
    response = model.generate_content(prompt)
    
    print("\n✅ Response received!")
    print(f"Raw response:\n{response.text}\n")
    
    # Try to parse JSON
    response_text = response.text.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    analysis = json.loads(response_text)
    print("✅ JSON parsed successfully!")
    print(json.dumps(analysis, indent=2))
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
