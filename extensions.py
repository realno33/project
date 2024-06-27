from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_Login import LoginManager


app = Flask(__name__)
app.config["SECRET_KEY"] ="sdafgertinko!@tufel"
app.config['UPLOAD_FOLDER'] = 'uploads/'


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
db = SQLAlchemy(app)



login_manager = LoginManager(app)