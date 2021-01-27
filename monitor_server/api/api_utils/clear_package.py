import re



def clear_package_name(fullname):
    # dev_helloworld_v0.1.0.tar
    pattern = "([a-zA-Z]\w*)_v([0-9]+)\.([0-9]+)\.([0-9]+).(\w+)"
    res = re.match(pattern, fullname)
    if not res:
        return None, "format error"
    try:
        package_name, main_version, second_version, third_version, suffix = res.groups()
        main_version = int(main_version)
        second_version = int(second_version)
        third_version = int(third_version)
        return (package_name, main_version, second_version, third_version, suffix),""
    except Exception as e:
        print("invalid input :%s", fullname)
        return None, "format error"


def clear_package_path(path):
    import os
    if not path.startswith("/"):
        path = os.path.join("/", path)
    if not os.path.isabs(path):
        return None,"format error"
    if len(path) >= 200:
        return None, "too long"
    return path,""



if __name__ == "__main__":
    pattern = "([a-zA-Z]\w*) ([0-9]+)\.([0-9]+)\.([0-9]+)"
    res = re.match(pattern,"hello 123.12.23")
    print(res)
    print(res.groups())
    import os
    res = clear_package_path("sadad/./_\\\\21312/  /")
    print(res)