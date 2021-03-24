import sys,io,os
print(sys)

original_import = sys.modules["builtins"].__import__

def xx(*args,**kwargs):
    # print(args, kwargs)
    res = original_import(*args,**kwargs)
    if args[0] == "hello":
        res.hello = res.hehe
    return res

sys.modules["builtins"].__import__ = xx
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
        with io.open_code(filename) as fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)

mainfile = sys.argv[1]
r= MyRunner()
f = os.path.realpath(mainfile)
print(f)
# m="imp"
# import imp
# r.run_module(m)
r.run_script(f)