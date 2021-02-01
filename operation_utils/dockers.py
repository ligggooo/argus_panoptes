import requests
import json
import docker
import traceback

def get_json_response(url,params={}):
    res = requests.get(url,**params)
    # print(res.content)
    data = json.loads(res.content)
    return data


def get_docker_images():
    # data= get_json_response("http://172.16.100.51:5000/v2/_catalog")
    # images = data["repositories"]
    # for x in images:
    #     d= get_json_response("http://172.16.100.51:5000/v2/%s/tags/list"%x)
    #     for tag in d["tags"]:
    #         print("172.16.100.51:5000/%s:%s"%(x,tag))
    class Image:
        def __init__(self,tag,size_in_mb):
            self.tag = tag
            self.size_in_mb = size_in_mb

    images = {}
    try:
        client = docker.DockerClient(base_url="http://172.16.100.51:2375",timeout=2)
        for img in client.images.list():
            full_name = img.tags[0]
            if "/" in full_name:
                name = full_name.split("/")[1]
            else:
                name = full_name
            size_in_MB = int(img.attrs["Size"]/1024/1024)
            images[name]=Image(full_name,size_in_MB)
        return images
    except Exception as e:
        print(img.tags)
        traceback.print_exc()
        return None


def get_docker_containers(ip,port):
    client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
    for c in client.containers.list(all=True):
        print(c)
        print(c.attrs)


def docker_clients():
    client = docker.DockerClient(base_url="http://172.16.100.52:2375")
    docker_version = client.version()
    #print(docker_version)
    #for cont in client.containers.list():
        #print(cont,cont.status,cont.image)# ,cont.attrs)
    for img in client.images.list():
        name = img.tags[0]
        size_in_MB = img.attrs["Size"]/1024/1024
        print(img)
    # get_docker_images()
    # client.images.pull("172.16.100.51:5000/hello-world","v1")

def create_container(ip,port,image_name,tag,container_name,command):
    client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
    images = client.images.list()
    print(images)
    c= client.containers.create(image="%s:%s"%(image_name,tag),command=command,name=container_name)
    print(c, dir(c))
    c.run()


if __name__ == '__main__':
    #get_docker_images()
    #
    #
    # docker_clients()
    # get_docker_containers("172.16.100.52",2375)
    create_container("172.16.100.52",2375,"172.16.100.51:5000/hello-world","v1","xx","/hello")