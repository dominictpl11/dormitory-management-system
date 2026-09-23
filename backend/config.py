import os
import secrets
from datetime import timedelta

# Get the directory of this config file
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dormitory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
