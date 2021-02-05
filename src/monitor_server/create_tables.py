from monitor_server import db
from models.model_001_test import ProcessState
from models.model_002_package import SoftPackage



def create_all():
    db.create_all()

create_all()