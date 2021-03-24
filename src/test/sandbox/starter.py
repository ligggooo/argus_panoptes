import sys,io,os
print(sys)
from starter_conf import _starter_conf

original_import = sys.modules["builtins"].__import__

from deco_module1 import deco_module


def my_import(*args,**kwargs):
    # print(args, kwargs)
    module_cache = dict()
    module_name = args[0]
    print("lee import ---------------", module_name)
    if module_name in module_cache:
        return module_cache.get(module_name)
    ret_module = original_import(*args, **kwargs)
    to_deco = _starter_conf.get_to_deco()
    if module_name in to_deco:
        print("替换", to_deco.get(module_name))
        deco_module(ret_module, to_deco.get(module_name))
    module_cache[module_name] = ret_module
    return ret_module


sys.modules["builtins"].__import__ = my_import
__builtins__ = sys.modules["builtins"]


class MyRunner:
    def __init__(self) -> None:
        pass

    def canonic(self, filename):
        import os
        """Return canonical form of filename.

        For real filenames, the canonical form is a case-normalized (on
        case insensitive filesystems) absolute path.  'Filenames' with
        angle brackets, such as "<stdin>", generated in interactive
        mode, are returned unchanged.
        """
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
            "__builtins__": __builtins__,
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

    def run_script(self, filename):
        # The script has to run in __main__ namespace (or imports from
        # __main__ will break).
        #
        # So we clear up the __main__ and set several special variables
        # (this gets rid of pdb's globals and cleans old variables on restarts).
        import __main__
        import sys,os
        # __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": sys.modules["builtins"],
                                 })

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = False
        with open(filename) as fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)


# mainfile = sys.argv[1]

mainfile = "pdb_t.py"
r= MyRunner()
f = os.path.realpath(mainfile)
print(f)
# m="imp"
# import imp
# r.run_module(m)
print("start -------------------")
r.run_script(f)
