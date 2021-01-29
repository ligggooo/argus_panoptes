import requests
import json
import docker

def get_json_response(url,params={}):
    res = requests.get(url,**params)
    # print(res.content)
    data = json.loads(res.content)
    return data


def get_docker_images():
    data= get_json_response("http://172.16.100.51:5000/v2/_catalog")
    images = data["repositories"]
    for x in images:
        print("--------------------")
        d= get_json_response("http://172.16.100.51:5000/v2/%s/tags/list"%x)
        for tag in d["tags"]:
            print("172.16.100.51:5000/%s:%s"%(x,tag))



def docker_clients():
    client = docker.DockerClient(base_url="http://172.16.100.52:2375")
    docker_version = client.version()
    #print(docker_version)
    #for cont in client.containers.list():
        #print(cont,cont.status,cont.image)# ,cont.attrs)
    for img in client.images.list():
        print(img)
    # get_docker_images()
    # client.images.pull("172.16.100.51:5000/hello-world","v1")

if __name__ == '__main__':
    get_docker_images()
    #
    #
    docker_clients()