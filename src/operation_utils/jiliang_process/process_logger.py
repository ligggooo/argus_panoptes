import logging
from logging import handlers
from logging import Formatter


proc_mon_logger = logging.getLogger()
proc_mon_logger.setLevel(logging.DEBUG)

fh = logging.handlers.TimedRotatingFileHandler(filename="test.log", encoding="utf-8")
sh = logging.StreamHandler()

fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
fh.setFormatter(fmt)
sh.setFormatter(fmt)

proc_mon_logger.addHandler(fh)
proc_mon_logger.addHandler(sh)


