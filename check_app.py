"""Quick check that app initializes correctly"""
import sys
sys.path.insert(0, 'c:\\Users\\ishit\\HealBuddy')

from app import model, db, app

print(f"Model initialized: {model is not None}")
print(f"Model type: {type(model)}")
print(f"Database initialized: {db is not None}")
print(f"App initialized: {app is not None}")

# Test if model works
if model:
    try:
        response = model.generate_content("Test")
        print(f"✅ Model is working! Response: {response.text[:50]}...")
    except Exception as e:
        print(f"❌ Model error: {e}")
