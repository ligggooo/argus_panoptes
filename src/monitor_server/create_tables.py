'''

'''
import sys
sys.path.insert(0,".")
from monitor_server.models.model_001_test import create_all as c1
from monitor_server.models.model_002_package import create_all as c2
from monitor_server.models.model_003_machines import create_all as c3
c3()
from monitor_server.models.model_004_dockers import create_all as c4
from monitor_server.models.model_005_deploy import create_all as c5
from monitor_server.models.model_006_tasks import create_all as c6

def create_all():
    '''

    :return:
    '''
    c1()
    c2()
    c3()
    c4()
    c5()
    c6()


create_all()
