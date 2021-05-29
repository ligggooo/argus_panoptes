import requests
import json
import docker
import traceback
import tarfile
import os
from operation_utils.file import get_tmp_data_dir
import uuid
from threading import Lock

# repo_addr = "http://10.130.160.114:2375"
# repo_addr = "http://192.168.31.110:2375"
repo_addr = "http://172.16.100.51:2375"
repo_addr_host = "172.16.100.51:5000"
repo_addr2 = "http://172.16.101.220:2375"

_tmp_data_dir = get_tmp_data_dir()
CHUNK_SIZE = 2048 * 1024


def get_json_response(url, params={}):
    res = requests.get(url, **params)
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
        def __init__(self, tag, size_in_mb):
            self.tag = tag
            self.size_in_mb = size_in_mb

    images = {}
    try:
        client = docker.DockerClient(base_url=repo_addr, timeout=2)
        for img in client.images.list():
            full_name = img.tags[0]
            # if "/" in full_name:
            #     name = full_name.split("/")[1]
            # else:
            #     name = full_name
            size_in_MB = int(img.attrs["Size"] / 1024 / 1024)
            images[full_name] = Image(full_name, size_in_MB)
        return images
    except Exception as e:
        traceback.print_exc()
        return {}


def get_docker_containers(ip, port):
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_raw_id = db.Column(db.String(128), nullable=False, unique=False)
    container_name = db.Column(db.String(128), nullable=False, unique=False)
    command = db.Column(db.String(512), nullable=False, unique=False)
    image_id = db.Column(db.Integer, nullable=False, unique=False)
    machine_id = db.Column(db.Integer, nullable=False, unique=False)
    port_mapping = db.Column(db.String(128), nullable=True, unique=False)
    ---------------------------------
    {'Id': 'bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0', 'Created': '2021-04-25T02:56:17.610369777Z',
    'Path': 'sh', 'Args': ['/run.sh'], 'State': {'Status': 'running', 'Running': True, 'Paused': False, 'Restarting': False,
    'OOMKilled': False, 'Dead': False, 'Pid': 97324, 'ExitCode': 0, 'Error': '', 'StartedAt': '2021-04-25T03:06:10.197124016Z',
    'FinishedAt': '2021-04-25T03:05:28.681836785Z'}, 'Image': 'sha256:0f34a5becdf0fa49f1fc00fd5a0651aebc887c8573c4eb1d16ceabb848fadf89',
    'ResolvConfPath': '/var/lib/docker/containers/bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0/resolv.conf',
    'HostnamePath': '/var/lib/docker/containers/bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0/hostname',
    'HostsPath': '/var/lib/docker/containers/bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0/hosts',
    'LogPath': '/var/lib/docker/containers/bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0/bde3ec0b091b3d3ab82a0c0b8f2c17527697b25c7cbb3840cd77756cc40d71d0-json.log',
    'Name': '/test_container_141', 'RestartCount': 0, 'Driver': 'overlay2', 'Platform': 'linux', 'MountLabel': '', 'ProcessLabel': '',
    'AppArmorProfile': '', 'ExecIDs': ['9cbee9f0e145a3e60989902e9f8a2505334da67302534ca7647eaa66c9102676'],
    'HostConfig': {'Binds': None, 'ContainerIDFile': '', 'LogConfig': {'Type': 'json-file', 'Config': {}},
    'NetworkMode': 'default', 'PortBindings': None, 'RestartPolicy': {'Name': '', 'MaximumRetryCount': 0},
    'AutoRemove': False, 'VolumeDriver': '', 'VolumesFrom': None, 'CapAdd': None, 'CapDrop': None, 'Dns': None,
    'DnsOptions': None, 'DnsSearch': None, 'ExtraHosts': None, 'GroupAdd': None, 'IpcMode': 'shareable', 'Cgroup': '',
    'Links': None, 'OomScoreAdj': 0, 'PidMode': '', 'Privileged': False, 'PublishAllPorts': False, 'ReadonlyRootfs': False,
    'SecurityOpt': None, 'UTSMode': '', 'UsernsMode': '', 'ShmSize': 67108864, 'Runtime': 'runc', 'ConsoleSize': [0, 0], 'Isolation': '',
    'CpuShares': 0, 'Memory': 0, 'NanoCpus': 0, 'CgroupParent': '', 'BlkioWeight': 0, 'BlkioWeightDevice': None, 'BlkioDeviceReadBps': None,
    'BlkioDeviceWriteBps': None, 'BlkioDeviceReadIOps': None, 'BlkioDeviceWriteIOps': None, 'CpuPeriod': 0, 'CpuQuota': 0, 'CpuRealtimePeriod': 0,
    'CpuRealtimeRuntime': 0, 'CpusetCpus': '', 'CpusetMems': '', 'Devices': None, 'DeviceCgroupRules': None, 'DiskQuota': 0, 'KernelMemory': 0, 'MemoryReservation': 0,
    'MemorySwap': 0, 'MemorySwappiness': None, 'OomKillDisable': False, 'PidsLimit': 0, 'Ulimits': None, 'CpuCount': 0, 'CpuPercent': 0, 'IOMaximumIOps': 0,
    'IOMaximumBandwidth': 0}, 'GraphDriver':
    {'Data': {'LowerDir': '/var/lib/docker/overlay2/b3405894c6b0a5be1f5690792b3ff43a3ea33b0dec16aff20e626c1b4ad0585c-init/diff:/var/lib/docker/overlay2/10239d502c23a7dc7c3ac6c60a4f9523d8c9784190a3a4bc97433fad7b0558ca/diff', 'MergedDir': '/var/lib/docker/overlay2/b3405894c6b0a5be1f5690792b3ff43a3ea33b0dec16aff20e626c1b4ad0585c/merged',
    'UpperDir': '/var/lib/docker/overlay2/b3405894c6b0a5be1f5690792b3ff43a3ea33b0dec16aff20e626c1b4ad0585c/diff', 'WorkDir': '/var/lib/docker/overlay2/b3405894c6b0a5be1f5690792b3ff43a3ea33b0dec16aff20e626c1b4ad0585c/work'}, 'Name': 'overlay2'}, 'Mounts': [], 'Config': {'Hostname': 'bde3ec0b091b', 'Domainname': '', 'User': '', 'AttachStdin': True, 'AttachStdout': True, 'AttachStderr': True, 'Tty': False, 'OpenStdin': True, 'StdinOnce': True, 'Env': ['HOST_IP=172.16.100.141', 'PATH_MAP=/app/inte_dir/test_container_141', 'CONTAINER_NAME=test_container_141'], 'Cmd': ['sh', '/run.sh'], 'Image': '172.16.100.51:5000/image_20201218', 'Volumes': None, 'WorkingDir': '', 'Entrypoint': None, 'OnBuild': None, 'Labels': {}}, 'NetworkSettings': {'Bridge': '', 'SandboxID': '354cf5be118dbc6468a47bae975c90d28458cb57c5c0417b5975f8cf55e52a83', 'HairpinMode': False, 'LinkLocalIPv6Address': '', 'LinkLocalIPv6PrefixLen': 0, 'Ports': {}, 'SandboxKey': '/var/run/docker/netns/354cf5be118d', 'SecondaryIPAddresses': None, 'SecondaryIPv6Addresses': None, 'EndpointID': '4b24afefe821effd65da832635202a8cb5e1563419ff58508227eab7f78cab6f', 'Gateway': '172.17.0.1', 'GlobalIPv6Address': '', 'GlobalIPv6PrefixLen': 0, 'IPAddress': '172.17.0.2', 'IPPrefixLen': 16, 'IPv6Gateway': '', 'MacAddress': '02:42:ac:11:00:02', 'Networks': {'bridge': {'IPAMConfig': None, 'Links': None, 'Aliases': None, 'NetworkID': '6e1f9a992aa871b5fcb7601f6056c3450f3b9535339423433edadab4faf1f7e4', 'EndpointID': '4b24afefe821effd65da832635202a8cb5e1563419ff58508227eab7f78cab6f', 'Gateway': '172.17.0.1', 'IPAddress': '172.17.0.2', 'IPPrefixLen': 16, 'IPv6Gateway': '', 'GlobalIPv6Address': '',
    'GlobalIPv6PrefixLen': 0, 'MacAddress': '02:42:ac:11:00:02', 'DriverOpts': None}}}}

    """
    client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
    res = []
    for c in client.containers.list(all=True):
        print(c)
        print(c.attrs)
        res.append({
            "container_raw_id": c.id,
            "container_name": c.name,
            "command": c.attrs["Config"]["Cmd"],
            "image_name": c.attrs["Config"]["Image"],
            "host_ip": ip,
            "port_mapping": c.attrs["NetworkSettings"]["Ports"],
        })
    return res


def docker_clients():
    client = docker.DockerClient(base_url=repo_addr)
    docker_version = client.version()
    # print(docker_version)
    # for cont in client.containers.list():
    # print(cont,cont.status,cont.image)# ,cont.attrs)
    for img in client.images.list():
        name = img.tags[0]
        size_in_MB = img.attrs["Size"] / 1024 / 1024
        print(img)
    # get_docker_images()
    # client.images.pull("172.16.100.51:5000/hello-world","v1")


def pull_image(ip, port, image_name):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        # images = client.images.list()
        # print(images)
        c = client.images.pull(image_name, all_tags=True)
        # print(c, dir(c))
        # c.run()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)
    return c, None


def create_container(ip, port, image_name_tag, container_name, command, port_mapping):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        # images = client.images.list()
        # print(images)
        c = client.containers.create(stdin_open=True, image=image_name_tag, command=command,
                                     name=container_name, ports=port_mapping,
                                     environment={"HOST_IP": ip,
                                                  "PATH_MAP": "/app/inte_dir/" + container_name,
                                                  "CONTAINER_NAME": container_name
                                                  }, )
        # print(c, dir(c))
        # c.run()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)
    return c, None


def init_docker_container(host_ip, container_name, dockerimage, command='/bin/bash'):
    client = docker.APIClient(base_url='tcp://' + host_ip + ':2375')
    client.images()
    client.create_container(stdin_open=True,
                            environment={"HOST_IP": host_ip,
                                         "PATH_MAP": "/app/inte_dir/" + container_name},
                            name=container_name,
                            host_config=client.create_host_config(mem_limit='24G', memswap_limit='32G'),
                            image=dockerimage,
                            command=command)
    client.start(container_name)
    tmp_exec = client.exec_create(container_name, ["mkdir", "-p", "/app/inte_dir/" + container_name])
    client.exec_start(tmp_exec.get('Id'))

    # ssh_cp(host_ip, 22, "root", "P2sswd123", container_name, "/app/inte_dir/projects_codes/",
    #        "/app/inte_dir/" + container_name)
    # client.stop(container_name)
    client.start(container_name)


def get_container(ip, port, container_id):
    client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
    c = client.containers.get(container_id=container_id)
    return c


def get_container_with_log(ip, port, container_id):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port), timeout=0.5)
        # images = client.images.list()
        # print(images)
        c = client.containers.get(container_id=container_id, )
        logs = c.logs(timestamps=True, tail=20).decode("utf-8")
        # print(c, dir(c))
        # c.run()
    except Exception as e:
        traceback.print_exc()
        return None, str(e)
    return c, logs


def rename_container(ip, port, container_id, new_name):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        c = client.containers.get(container_id=container_id)
        if new_name != c.name:
            c.rename(new_name)
        msg = None
    except Exception as e:
        traceback.print_exc()
        msg = str(e)
    return c, msg


def rm_container(ip, port, container_id):
    try:
        client = docker.DockerClient(base_url="http://%s:%d" % (ip, port))
        c = client.containers.get(container_id=container_id)
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
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def stop_container(ip, port, container_id):
    try:
        c = get_container(ip, port, container_id)
        if c:
            c.stop(timeout=2)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def restart_container(ip, port, container_id):
    try:
        c = get_container(ip, port, container_id)
        if c:
            c.restart(timeout=5)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def remove_container(ip, port, container_id):
    try:
        c = get_container(ip, port, container_id)
        if c:
            c.remove(v=True, force=True)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


def cp_file_2_container(ip, port, container_id, file_path):
    try:
        c = get_container(ip, port, container_id)
        if c:
            data = open(file_path, "rb").read()
            c.put_archive("/", data)
        return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def container_exec(ip, port, container_id, command):
    try:
        c = get_container(ip, port, container_id)
        if c:
            # exec_run(self, cmd, stdout=True, stderr=True, stdin=False, tty=False,
            #          privileged=False, user='', detach=False, stream=False,
            #          socket=False, environment=None, workdir=None, demux=False)
            ret = c.exec_run(command)
            if ret.exit_code == 0:
                return "success", ret.output.decode("utf-8")
            else:
                return "failed", ret.output.decode("utf-8")
        else:
            return "failed", "cannot find this container"
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


def exec_cmd(ip, port, container_id, cmd):
    try:
        c = get_container(ip, port, container_id)
        if c:
            res = c.exec_run(cmd)
            if res.exit_code != 0:
                ret = "failed", res[1]
            else:
                ret = "success", res[1]
        else:
            ret = "failed", "cannot find this container"
        return ret
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


cp_lock = Lock()


def tar_and_cp_file_2_container(ip, port, container_id, file_path, tmp_dir=_tmp_data_dir):
    try:
        with cp_lock:
            c = get_container(ip, port, container_id)
            if c:
                tmp_tar_name = str(uuid.uuid4()) + ".tar"
                tar = tarfile.open(os.path.join(tmp_dir, tmp_tar_name), mode="w")

                os.chdir(tmp_dir)
                tar.add(file_path)
                tar.close()
                data = open(tmp_tar_name, "rb").read()
                c.put_archive("/", data)
            return "success", None
    except Exception as e:
        traceback.print_exc()
        return "success", str(e)


write_lock = Lock()


def write_content_2_container(ip, port, container_id, content, file_path="/run.sh"):
    try:
        with write_lock:
            c = get_container(ip, port, container_id)
            if c:
                tmp_dir = os.path.join(_tmp_data_dir, str(uuid.uuid4()))
                os.makedirs(tmp_dir)
                tmp_tar_name = "data.tar"
                target_file_name = os.path.split(file_path)[1]
                os.chdir(tmp_dir)

                with open(target_file_name, "w", newline="\n") as f:
                    f.write(content)
                tar = tarfile.open(os.path.join(tmp_tar_name), mode="w:tar")
                tar.add(target_file_name)
                tar.close()
                data = open(tmp_tar_name, "rb").read()
                c.put_archive("/", data)
            return "success", None
    except Exception as e:
        traceback.print_exc()
        return "failed", str(e)


def cp_file_from_container(ip, port, container_id, file_path, tmp_dir_root=_tmp_data_dir):
    try:
        c = get_container(ip, port, container_id)
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
    # get_docker_images()
    #
    #
    # docker_clients()
    # get_docker_containers("172.16.100.52",2375)
    # c= create_container("10.130.160.114",2375,"image_20201024:latest","xx","/hello")
    # c,err = get_container_with_log("10.130.160.114",2375,"xx")
    #
    # print(c.id,c.name)
    # c, err = rename_container("10.130.160.114", 2375, "xx","zzzzzz")
    # print(c.id, c.name)
    #
    # rm_container("10.130.160.114",2375,"xxxxxx")
    # start_container("10.130.160.114",2375,"xx")
    host = "10.130.160.114"
    host = "172.16.101.119"
    image = "image_20201228:latest"
    # init_docker_container(host, "test005", image, command='/bin/bash')
    # c = create_container(host, 2375, image, "test007", "/bin/bash")

    #
    # cp_file_2_container(host, 2375, "mgt2", _tmp_data_dir+"/test.tar")
    # tar_and_cp_file_2_container(host, 2375, "mgt2", "run.sh")
    # a,b = cp_file_from_container(host, 2375, "mgt2", "/zzrun.sh")
    # print(a,b)
    # write_content_2_container(host, 2375, "test_copy", "sleep 100\n", "/run.sh")

    # container_exec(host, 2375, "jlmonitor", "lx")
    # pull_image(host, 2375, "172.16.100.51:5000/image_20201218")
    xx = exec_cmd("172.16.100.51", 2375, "jiliang_core", "ls /xx")
    print(xx)
