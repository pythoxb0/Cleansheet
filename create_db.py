# create_db.py
import os
from app import create_app, db

# Set environment variables
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
os.environ['DATABASE_URL'] = 'sqlite:///app.db'

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")