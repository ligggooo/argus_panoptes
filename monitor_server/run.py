from flask import Flask, url_for
from flask import render_template
from flask import request

from monitor_server import app

from monitor_server.api import server_views_products
app.register_blueprint(server_views_products.api_group1)


if __name__ == '__main__':
    app.run()

