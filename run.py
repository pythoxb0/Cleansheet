# run.py
import os
from app import create_app, db
from app.models import User, File

# Disable dotenv loading by Flask
os.environ['FLASK_SKIP_DOTENV'] = '1'

app = create_app()

# Manual configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'File': File}

if __name__ == '__main__':
    app.run(debug=True)