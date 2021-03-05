import sys
import os
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(src_path)
sys.path.append(os.path.join(src_path, "monitor_server"))

from monitor_server import app

from monitor_server.api import api_group1,api_group2,api_group3,api_group4,api_group5,api_group6

app.register_blueprint(api_group1)
app.register_blueprint(api_group2)
app.register_blueprint(api_group3)
app.register_blueprint(api_group4)
app.register_blueprint(api_group5)
app.register_blueprint(api_group6)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=60010)
    #app.run()

