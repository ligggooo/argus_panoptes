import os
from operation_utils.file import get_parent_dir

SRC_ROOT = get_parent_dir(os.path.abspath(__file__), 2)


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
    # STATIC_FOLDER = '../static'
    # STATIC_URL_PATH = '/statics'


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True


# class TestingConfig(Config):
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI="sqlite:///my_db.sqlite"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig2(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="postgresql://postgres:123456@10.130.160.114:60030/my_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TASK_TRACK_CACHE = False
    TASK_RECORDER_URL = "http://127.0.0.1:60010/record_tasks"
    TASK_UNIQUE_ID_URL = "http://127.0.0.1:60010/task_unique_id"

config = TestingConfig2