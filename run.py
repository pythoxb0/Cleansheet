import os
# COMPLETELY disable Flask's .env loading - must be at VERY top
os.environ['FLASK_SKIP_DOTENV'] = '1'

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)