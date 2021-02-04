

def port_mapping_str2list(mapping_str):
    class Mapping:
        def __init__(self,port): # lazy solution
            self.from_port = port
            self.to_port = port

        @property
        def show(self):
            return "%d --> %d"%(self.from_port,self.to_port)

    ret = []
    msg = None
    if not mapping_str:
        pass
    else:
        try:
            tokens = mapping_str.split(",")
            for t in tokens:
                mapping = Mapping(int(t))
                ret.append(mapping)
        except Exception as e:
            ret=-1
            msg = str(e)
    return ret, msg

def port_mapping_list2dict(port_mapping_list):
    ret ={}
    for pp in port_mapping_list:
        key = "%d/tcp"%pp.from_port
        ret.update({key:pp.to_port})
    return ret

def port_mapping_str2dict(mapping_str):
    ret,_ = port_mapping_str2list(mapping_str)
    ret = port_mapping_list2dict(ret)
    return  ret

def check_ports(available_ports_objs,port_mappings):
    invalid_ports = []
    ret = 0
    msg = None
    available_ports = [p.port_num for p in available_ports_objs]
    if not available_ports and port_mappings:
        ret = -1
        msg = "当前机器无可用端口"
        return ret, msg
    for pp in port_mappings:
        if pp.to_port not in available_ports:
            invalid_ports.append(str(pp.to_port))
            ret =-1
    if ret ==-1:
        msg = 'invalid ports : '+ ",".join(invalid_ports)+" valid ports : " \
              + ",".join([str(x) for x in available_ports])
    return ret,msg


def update_ports(available_ports_objs, port_mappings):
    port_mappings_port_nums = [pp.to_port for pp in port_mappings]
    for apo in available_ports_objs:
        if apo.port_num in port_mappings_port_nums:
            apo.available = 0
