from flask import Flask, url_for
from flask import render_template
from flask import request

from monitor_server import app

from monitor_server.api import api_group1,api_group2,api_group3,api_group4,api_group5

app.register_blueprint(api_group1)
app.register_blueprint(api_group2)
app.register_blueprint(api_group3)
app.register_blueprint(api_group4)
app.register_blueprint(api_group5)


if __name__ == '__main__':
    # app.run(host="172.16.5.148",port=5000)
    app.run()

