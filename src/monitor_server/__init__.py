from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from .settings.conf import TestingConfig
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.config.from_object("monitor_server.settings.conf.TestingConfig2")
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
# 将db注册到app中（在内部读取配置文件）    　　
app.config["SQLALCHEMY_ECHO"] = True


db = SQLAlchemy(app)







