import sys
import subprocess
import importlib



import os
res= os.popen("ipconfig").read()
res= subprocess.Popen("ipconfig", stdout=subprocess.PIPE,shell=True)
# res.communicate()
print(res.stdout.read().decode("gbk"))