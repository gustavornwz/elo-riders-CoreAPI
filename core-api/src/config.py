# core-api/src/config.py

import os

# get base directory
basedir = os.path.join(os.path.dirname(__file__), '..')

# main config class
class Config:
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
    ELO_MODEL_NAME = os.getenv('ELO_MODEL_NAME', 'motorcycle-elo')

# development config
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or     'sqlite:///' + os.path.join(basedir, 'src/db/coreapi_dev.sqlite')

# testing config
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or     'sqlite:///' + os.path.join(basedir, 'src/db/coreapi_test.sqlite')
    PRESERVE_CONTEXT_ON_EXCEPTION = False

# production config
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or     'sqlite:///' + os.path.join(basedir, 'src/db/coreapi_prod.sqlite')

# dictionary of config classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
