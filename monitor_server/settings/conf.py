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


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="sqlite:///my_db.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False