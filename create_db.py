# create_db.py
import os
import sys
from app import create_app, db
from app.models import User, File

# Set environment variables
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
os.environ['DATABASE_URL'] = 'sqlite:///app.db'
os.environ['FLASK_SKIP_DOTENV'] = '1'

app = create_app()

with app.app_context():
    try:
        # Drop all existing tables and create new ones
        db.drop_all()
        db.create_all()
        
        # Verify the username column exists - using new SQLAlchemy API
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(user)")).fetchall()
            columns = [col[1] for col in result]
            print("Columns in user table:", columns)
            
            if 'username' in columns:
                print("✅ Database created successfully with username column!")
            else:
                print("❌ Username column missing!")
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Trying alternative approach...")
        
        # Alternative approach
        db.create_all()
        print("✅ Database tables created (alternative method)")