from flask import Flask, url_for
from flask import render_template
from flask import request

from monitor_server import app


if __name__ == '__main__':
    app.run()

