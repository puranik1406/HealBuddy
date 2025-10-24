#!/usr/bin/env python3
"""
Create fresh database for HealBuddy
"""

from app import app, db

def create_fresh_database():
    """Create a fresh database with all tables"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Created fresh database with all tables")
        print("📁 Database file: instance/healbuddy.db")
        
        # Show what tables were created
        print("\n📋 Tables created:")
        print("- users (for patients, doctors, hospitals)")
        print("- health_records (for medical documents)")
        print("- consultations (for AI consultations)")

if __name__ == "__main__":
    print("🚀 Creating fresh HealBuddy database...")
    create_fresh_database()
    print("\n🎉 Database creation complete!")
    print("You can now start the Flask app and register new users.")



