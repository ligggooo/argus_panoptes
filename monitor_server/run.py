from flask import Flask, url_for
from flask import render_template
from flask import request

from monitor_server import app

from monitor_server.api import api_group1,api_group2,api_group3

app.register_blueprint(api_group1)
app.register_blueprint(api_group2)
app.register_blueprint(api_group3)


if __name__ == '__main__':
    app.run()

