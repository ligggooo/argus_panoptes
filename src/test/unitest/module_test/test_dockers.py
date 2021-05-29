import unittest

from api_utils.portmapping_parser import port_mapping_str2dict
from operation_utils.dockers import create_container, remove_container, exec_cmd, get_docker_containers


class DockerTestCase(unittest.TestCase):
    def test_create(self):
        ip = "10.130.160.114"
        port = 2375
        container_id = "my_test_container123"
        remove_container(ip, port, container_id)
        port_mapping = port_mapping_str2dict("12313,21313")
        c, msg = create_container(ip, port, "image_20201024:latest", container_id, "/bin/sh",
                                  port_mapping=port_mapping)
        self.assertTrue(msg is None)
        print(c.logs(timestamps=True))
        c.start()
        print(c.logs(timestamps=True))

    def test_exec(self):
        ip = "10.130.160.114"
        port = 2375
        container_id = "my_test_container123"
        status, res = exec_cmd(ip, port, container_id, "env")
        print(status, res)
        data = {}
        for token in res.decode("ascii").split("\n"):
            pair = token.split("=")
            if len(pair) <= 1:
                continue
            var_name, value = pair
            data.update({var_name: value})
        print(data)
        self.assertEqual(data.get("HOST_IP"), ip)
        self.assertEqual(data.get("CONTAINER_NAME"), container_id)


    def test_get_container(self):
        res = get_docker_containers("10.130.160.114", 2375)

if __name__ == '__main__':
    unittest.main()
