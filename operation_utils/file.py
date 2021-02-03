import os

def get_parent_dir(path,levels):
    while path.endswith("/") or path.endswith("\\"):
        path = path[:-1]
    while levels>=0:
        path,_ = os.path.split(path)
        levels -=1
    return path

__this_file = __file__

def get_data_dir():
    src_root = get_parent_dir(os.path.abspath(__this_file),1)
    data_root = os.path.join(src_root, "data")
    return data_root if os.path.exists(data_root) else None

def get_tmp_data_dir():
    src_root = get_parent_dir(os.path.abspath(__this_file),1)
    data_root = os.path.join(src_root, "data_tmp",)
    if not os.path.exists(data_root):
        os.makedirs(data_root)
    return data_root


if __name__ == "__main__":
    res = get_parent_dir("./esc/sdsd/aa/1",2)
    print(res)
    print(get_data_dir())




