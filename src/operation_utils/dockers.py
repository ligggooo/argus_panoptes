import requests
import json
import docker
import traceback
import tarfile
import os
from operation_utils.file import get_tmp_data_dir
import uuid


_tmp_data_dir = get_tmp_data_dir()
CHUNK_SIZE = 2048*1024


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
        client = docker.DockerClient(base_url="http://10.130.160.114:2375",timeout=2)
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


def __get_container(ip,port,container_id):
    client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
    c = client.containers.get(container_id=container_id)
    return c


def create_container(ip, port, image_name_tag, container_name, command, port_mapping):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        # images = client.images.list()
        # print(images)
        c= client.containers.create(stdin_open=True,image=image_name_tag, command=command,
                                    name=container_name, ports=port_mapping)
        # print(c, dir(c))
        # c.run()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)
    return c, None


def init_docker_container(host_ip, container_name, dockerimage,command='/bin/bash'):
    client = docker.APIClient(base_url='tcp://' + host_ip + ':2375')
    client.images()
    client.create_container(stdin_open=True,
                            environment={"HOST_IP": host_ip,
                                         "PATH_MAP": "/app/inte_dir/" + container_name},
                            name=container_name,
                            host_config=client.create_host_config(mem_limit='24G',memswap_limit='32G'),
                            image=dockerimage,
                            command=command)
    client.start(container_name)
    tmp_exec = client.exec_create(container_name, ["mkdir", "-p", "/app/inte_dir/" + container_name])
    client.exec_start(tmp_exec.get('Id'))

    # ssh_cp(host_ip, 22, "root", "P2sswd123", container_name, "/app/inte_dir/projects_codes/",
    #        "/app/inte_dir/" + container_name)
    # client.stop(container_name)
    client.start(container_name)




def get_container(ip,port,container_id):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        # images = client.images.list()
        # print(images)
        c= client.containers.get(container_id=container_id)
        logs = c.logs(timestamps=True, tail=20).decode("utf-8")
        # print(c, dir(c))
        # c.run()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)
    return c, logs


def rename_container(ip,port,container_id,new_name):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        c= client.containers.get(container_id=container_id)
        if new_name!=c.name:
            c.rename(new_name)
        msg = None
    except Exception as e:
        traceback.print_exc()
        msg = str(e)
    return c, msg


def rm_container(ip,port,container_id):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        c= client.containers.get(container_id=container_id)
        if c:
            c.remove()
        return None
    except Exception as e:
        traceback.print_exc()
        return str(e)


def start_container(ip, port, container_id):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        c = client.containers.get(container_id=container_id)
        if c:
            c.start()
        return "success",None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def stop_container(ip, port, container_id):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            c.stop(timeout=2)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def restart_container(ip, port, container_id):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            c.restart(timeout=5)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def remove_container(ip, port, container_id):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            c.remove(v=True,force=True)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


def cp_file_2_container(ip, port, container_id, file_path):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            data = open(file_path,"rb").read()
            c.put_archive("/",data)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


def tar_and_cp_file_2_container(ip, port, container_id, file_path):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            tmp_tar_name = str(uuid.uuid4())+".tar"
            tar = tarfile.open(os.path.join(_tmp_data_dir,tmp_tar_name), mode="w")

            os.chdir(_tmp_data_dir)
            tar.add(file_path)
            tar.close()
            data = open(tmp_tar_name,"rb").read()
            c.put_archive("/",data)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)

def write_content_2_container(ip, port, container_id, content, file_path="/run.sh"):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            tmp_dir = os.path.join(_tmp_data_dir, str(uuid.uuid4()))
            os.makedirs(tmp_dir)
            tmp_tar_name = "data.tar"
            target_file_name = os.path.split(file_path)[1]
            os.chdir(tmp_dir)

            with open(target_file_name,"w") as f:
                f.write(content)
            tar = tarfile.open(os.path.join(tmp_tar_name), mode="w")
            tar.add(target_file_name)
            tar.close()
            data = open(tmp_tar_name,"rb").read()
            c.put_archive("/",data)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def cp_file_from_container(ip, port, container_id, file_path,tmp_dir_root=_tmp_data_dir):
    try:
        c = __get_container(ip, port, container_id)
        if c:
            bits, stat = c.get_archive(file_path, chunk_size=CHUNK_SIZE)
            name = stat.get("name")
            tmp_dir = os.path.join(tmp_dir_root, str(uuid.uuid4()))
            os.makedirs(tmp_dir)
            tar_name = os.path.join(tmp_dir, name + ".tar")
            with open(tar_name, "wb") as f:
                for chunk in bits:
                    f.write(chunk)
            tar = tarfile.open(tar_name, mode="r")
            tar.extractall(path=tmp_dir)
            return "success", (tmp_dir, name)
        else:
            return "failed", "no such container"
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)

if __name__ == '__main__':
    #get_docker_images()
    #
    #
    # docker_clients()
    # get_docker_containers("172.16.100.52",2375)
    # c= create_container("10.130.160.114",2375,"image_20201024:latest","xx","/hello")
    # c,err = get_container("10.130.160.114",2375,"xx")
    #
    # print(c.id,c.name)
    # c, err = rename_container("10.130.160.114", 2375, "xx","zzzzzz")
    # print(c.id, c.name)
    #
    # rm_container("10.130.160.114",2375,"xxxxxx")
    # start_container("10.130.160.114",2375,"xx")

    host = "10.130.160.114"
    image = "image_20201024:latest"
    #init_docker_container(host, "test005", image, command='/bin/bash')
    # c = create_container(host, 2375, image, "test007", "/bin/bash")

    #
    #cp_file_2_container(host, 2375, "mgt2", _tmp_data_dir+"/test.tar")
    #tar_and_cp_file_2_container(host, 2375, "mgt2", "run.sh")
    # a,b = cp_file_from_container(host, 2375, "mgt2", "/zzrun.sh")
    # print(a,b)
    write_content_2_container(host, 2375, "mgt2", "ls alh\nfind / -name \"*.so\"", "/run.sh")