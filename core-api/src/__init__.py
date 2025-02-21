# core-api/src/__init__.py

from flask import Flask
from flask_migrate import Migrate
from src.config import config
from dotenv import load_dotenv
import os

from src.models import db
# from src.candidate.views import candidates_blueprint
from .user.views import users_blueprint, sensor_blueprint, elo_blueprint
from .events.views import events_blueprint


# app constructor
def create_app(config_name):
    app = Flask(__name__)

    # set config
    config_name = os.getenv('FLASK_ENV', 'development')

    # load .env file
    if config_name == 'development':
        env_file = '.env'
    elif config_name == 'testing':
        env_file = '.env.test'
    elif config_name == 'production':
        env_file = '.env.prod'
    else:
        env_file = '.env'

    load_dotenv(env_file)

    # set configuration
    if config_name == 'development':
        app.config.from_object(config[config_name])
    elif config_name == 'testing':
        app.config.from_object(config[config_name])
    elif config_name == 'production':
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config['default'])

    # init db
    db.init_app(app)

    # init migrate
    migrate = Migrate(app, db)
    print(f'Migrate initialized: {migrate}')
   
    # register blueprint
    app.register_blueprint(users_blueprint)
    app.register_blueprint(sensor_blueprint)
    app.register_blueprint(elo_blueprint)
    app.register_blueprint(events_blueprint)

    return app
