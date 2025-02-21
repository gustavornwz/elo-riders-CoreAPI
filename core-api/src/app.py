# core-api/src/app.py

from src import create_app
from flask_cors import CORS
from src.models import db
import logging
import os

from flask_jwt_extended import JWTManager

# app setup
app = create_app('default')
app_context = app.app_context()
app_context.push()
print(f"DB_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# logging setup
logging.basicConfig(level=logging.DEBUG)

# db setup
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
    # pass

# Cors
cors = CORS(app)

# JWT Auth
jwt = JWTManager(app)

# check-health-component at root level
@app.route('/ping', methods=['GET'])
def ping():
    app_name = os.getenv('FLASK_APP_NAME')
    return {"message":f"pong from {app_name} app"}