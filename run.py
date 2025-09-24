import os
from app import create_app, db
from app.models import User, File

# Disable dotenv
os.environ['FLASK_SKIP_DOTENV'] = '1'

app = create_app()

# Manual configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

# Auto-create tables on first deploy
with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'File': File}

if __name__ == '__main__':
    app.run()
