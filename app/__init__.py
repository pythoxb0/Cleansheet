from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import os
import logging
logging.basicConfig(level=logging.DEBUG)
# Try to load .env, but continue if it fails
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Note: Could not load .env file: {e}")

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # SECRET_KEY is REQUIRED for Flask sessions, CSRF, etc.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration with PostgreSQL fix
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Other important configs
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Email configuration (with defaults for development)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True 
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@cleansheet.com')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    with app.app_context():
        from app.routes import main as main_blueprint
        from app.auth import auth as auth_blueprint
        
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint)
     
    return app