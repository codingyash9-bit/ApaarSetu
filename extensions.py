"""
Flask extensions initialization for APAAR Nexus.
Instantiates database, login manager, and CSRF protection.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
