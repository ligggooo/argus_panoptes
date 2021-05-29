import sys
import os
import traceback
sys.path.append(r"/workspace/jiliang_monitor_pr/src")
sys.path.append(r"E:\workspace\jiliang_monitor_pr/src")
from jiliang_process.boot.starter_conf import get_starter_conf
from jiliang_process.boot.deco_module1 import deco_module
from jiliang_process.process_monitor import task_monitor


class MyRunner:
    def __init__(self) -> None:
        if getattr(sys.modules["builtins"].__import__, "runner_tag", None) is None:
            self.__original_import = sys.modules["builtins"].__import__
        else:
            raise Exception("两次初始化runner")
            pass

    def canonic(self, filename):
        import os
        if filename == "<" + filename[1:-1] + ">":
            return filename
        canonic = os.path.abspath(filename)
        canonic = os.path.normcase(canonic)
        return canonic

    def run_module(self, module_name):
        self._wait_for_mainpyfile = True
        self._user_requested_quit = False
        import runpy
        mod_name, mod_spec, code = runpy._get_module_details(module_name)
        self.mainpyfile = self.canonic(code.co_filename)
        import __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({
            "__name__": "__main__",
            "__file__": self.mainpyfile,
            "__package__": mod_spec.parent,
            "__loader__": mod_spec.loader,
            "__spec__": mod_spec,
            "__builtins__": sys.modules["builtins"],
        })
        self.run(code)

    def run(self, cmd, globals=None, locals=None):
        """Debug a statement executed via the exec() function.

        globals defaults to __main__.dict; locals defaults to globals.
        """
        if globals is None:
            import __main__
            globals = __main__.__dict__
        if locals is None:
            locals = globals
        # self.reset()
        if isinstance(cmd, str):
            cmd = compile(cmd, "<string>", "exec")
        try:
            exec(cmd, globals, locals)
        except Exception as e:
            raise e
        finally:
            self.quitting = True


    @task_monitor.cross_process_deco("脚本启动器")
    def run_script(self, filename, root_id=None, parent_id=None):
        import __main__
        import sys,os
        _starter_conf = get_starter_conf()
        os.chdir(os.path.split(filename)[0])
        filename = os.path.split(filename)[1]
        sys.path.insert(0, os.getcwd())
        print("lee_debug current", os.getcwd())
        def my_import(*args, **kwargs):
            # print(args, kwargs)
            # module_cache = dict()
            module_name = args[0]
            if module_name.startswith("dcs") or module_name.startswith("s3fs"):
                pass
            # print("lee import -------%s--------"%module_name)
            # if module_name in module_cache:
            #     print("lee done import cached ---%s---" % module_name)
            #     return module_cache.get(module_name)
            try:
                ret_module = self.__original_import(*args, **kwargs)
            except ImportError as e:
                # print("lee import ImportError -------%s--------"%module_name,e)
                # print(args,kwargs)
                raise e
            except Exception as e:
                # print("lee import Exception -------%s--------" % module_name,e)
                traceback.print_exc()
                return e
            finally:
                pass
            if len(args) <2 and len(module_name)>0:
                # print(args)
                # print("lee done import cached ---%s---" % module_name)
                # module_cache[module_name] = ret_module
                return ret_module
            else:
                info = args[1]
                if not info:  # 居然还有info传None的情况
                    info = {}
            if (not module_name) or info.get("__name__","") in ["unittest"]:
                # print("lee done import ---%s-------" % module_name)
                return ret_module
            module_deco_rules = _starter_conf.match(module_name)
            status = True
            if module_deco_rules:
                print("装饰模块", module_deco_rules)
                status = deco_module(ret_module,module_name, module_deco_rules)
            if status:
                # module_cache[module_name] = ret_module
                pass
            # print("lee done import ---%s-------" % module_name)
            return ret_module

        if getattr(sys.modules["builtins"].__import__, "runner_tag", None) is None:
            sys.modules["builtins"].__import__ = my_import
            sys.modules["builtins"].__import__.runner_tag = "replaced"


        # __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": sys.modules["builtins"],
                                 })

        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = False
        with open(filename,encoding="utf-8",) as fp:
            # content = compile(fp.read(), self.mainpyfile, 'exec')
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)


if __name__ == "__main__":
    print("start -------------------", sys.argv)
    if len(sys.argv) == 1:
        mainfile = "demo.py"
        path = os.path.dirname(os.path.abspath(__file__))
        f = os.path.join(path, mainfile)
        sys.argv = ["starter.py", "demo.py", '''{\"root_id\":\"\",\"parent_id\":\"\"}''']
    else:
        f = sys.argv[1]
    sys.argv = sys.argv[1:]

    # -----------------------------------------
    try:
        msg = sys.argv[1]
        root_id, parent_id, _ = task_monitor.extract_monitor_params_from_str(msg)
        print("lee_debug", root_id, parent_id)
    except Exception as e:
        raise e
        # root_id = None
        # parent_id = None
    # -----------------------------------------
    r = MyRunner()
    r.run_script(f,root_id=root_id, parent_id=parent_id)
