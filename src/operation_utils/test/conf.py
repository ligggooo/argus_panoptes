DEBUG = True
#dialect+driver://root:1q2w3e4r5t@127.0.0.1:3306/
DIALECT = 'mysql'
DRIVER='pymysql'
USERNAME = 'root'
PASSWORD = '1q2w3e4r5t'
HOST = '127.0.0.1'
PORT = 3306
DATABASE = 'db_demo1'

SQLALCHEMY_DATABASE_URI = "sqlite:///my_db.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = False
print(SQLALCHEMY_DATABASE_URI)