from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

from app.backend.routes import main as main_module

app.register_blueprint(main_module)
