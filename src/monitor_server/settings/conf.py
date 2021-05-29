import os
from operation_utils.file import get_parent_dir

SRC_ROOT = get_parent_dir(os.path.abspath(__file__), 2)


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
    TEMPLATES_AUTO_RELOAD = True
    # STATIC_FOLDER = '../static'
    # STATIC_URL_PATH = '/statics'
    host = ""
    port = 8080
    cache_size = 20

    @classmethod
    def TASK_RECORDER_URL(cls):
        return "%s/record_tasks" % cls.get_url()

    @classmethod
    def TASK_UNIQUE_ID_URL(cls):
        return "%s/task_unique_id" % cls.get_url()

    @classmethod
    def TASK_CHECK_URL(cls):
        return "%s/task_has_error" % cls.get_url()

    @classmethod
    def get_url(cls):
        return "http://%s:%d"%(cls.host, cls.port)


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    host = "172.16.5.148"
    port = 60012
    SQLALCHEMY_DATABASE_URI="sqlite:///my_db.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfigDev(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="postgresql://postgres:123456@10.130.160.114:60030/my_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_POOL_SIZE = 10
    DB_POOL_RECYCLE = 10
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size' : DB_POOL_SIZE,
        'pool_recycle' : DB_POOL_RECYCLE
    }
    TASK_TRACK_CACHE = False
    host = "172.16.5.148"
    port = 60010
    cache_size = 20



class TestingConfig3(Config):
    TESTING = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI="postgresql://lee:1122@192.168.31.110:5432/test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_POOL_SIZE = 10
    DB_POOL_RECYCLE = 10
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size' : DB_POOL_SIZE,
        'pool_recycle' : DB_POOL_RECYCLE
    }
    TASK_TRACK_CACHE = False
    host = "127.0.0.1"
    port = 60010


class TestingConfigProduct(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="postgresql://postgres:123456@10.130.160.114:60030/my_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_POOL_SIZE = 10
    DB_POOL_RECYCLE = 10
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size' : DB_POOL_SIZE,
        'pool_recycle' : DB_POOL_RECYCLE
    }
    TASK_TRACK_CACHE = False
    host = "172.16.101.220"
    port = 60010
    cache_size = 20


config = TestingConfigDev

class RedisConnWork:
    # host = '192.168.31.110'
    host = '172.16.100.53'
    pswd = '123456'
    port = 6379
    db = 0


class RedisConnTest:
    host = '127.0.0.1'
    port = 6379
    db = 0
    pswd = None


RedisConn = RedisConnWork
