from flask import Flask
import conf as config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
Base = declarative_base()


class Blog(db.Model):
    __tablename__ = 'blog'
    id  = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text,nullable=True)


db.create_all()