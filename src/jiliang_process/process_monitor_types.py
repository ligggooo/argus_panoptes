import enum


class StatePoint(enum.Enum):
    start = 0
    end = 1
    error = 2


class ProcessState(enum.Enum):
    unknown = -3
    record_incomplete = -2
    not_started_yet = -1
    running = 0
    # running_with_error = 0
    finished = 1
    # finished_with_error = 2
    failed = 2
    partially_finished = 3


class CallCategory(enum.Enum):
    root = -1
    normal = 0
    # loop = 1
    cross_thread = 2
    cross_process = 3
    # branch = 4