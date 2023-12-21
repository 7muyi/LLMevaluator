from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from config import config


app=Flask(__name__)

# Config
app.config.from_object(config["dev"])

db = SQLAlchemy(app)