from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    plan = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    files = db.relationship('File', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_process_file(self, row_count):
        """Check if user can process file based on their plan"""
        if self.plan == 'pro':
            return True
        return row_count <= 500  # Free tier limit
    def upgrade_to_pro(self):
        """Upgrade user to pro plan"""
        self.plan = 'pro'
        db.session.commit()
    
    def downgrade_to_free(self):
        """Downgrade user to free plan"""
        self.plan = 'free'
        db.session.commit()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    cleaned_filename = db.Column(db.String(255))
    s3_original_key = db.Column(db.String(255))
    s3_cleaned_key = db.Column(db.String(255))
    rows_original = db.Column(db.Integer)
    rows_cleaned = db.Column(db.Integer)
    operations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))