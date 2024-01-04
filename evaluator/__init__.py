from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from config import configs


app=Flask(__name__)

# Config
app.config.from_object(configs["development"])

db = SQLAlchemy(app)

from . import auth 