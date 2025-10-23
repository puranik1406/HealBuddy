"""Database update script to add preferred_hospitals column"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Try to add the column if it doesn't exist
        with db.engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            
            if 'preferred_hospitals' not in columns:
                print("Adding 'preferred_hospitals' column...")
                conn.execute(text("ALTER TABLE user ADD COLUMN preferred_hospitals TEXT"))
                conn.commit()
                print("✅ Column 'preferred_hospitals' added successfully!")
            else:
                print("✅ Column 'preferred_hospitals' already exists!")
        
        # Create any other missing tables
        db.create_all()
        print("✅ Database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
