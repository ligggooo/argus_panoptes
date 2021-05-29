import enum


class StatePoint(enum.Enum):
    """
    记录状态点的状态，是数据库原始记录中的状态
    """
    start = 0
    end = 1
    error = 2
    process_shutdown = 3


class ProcessState(enum.Enum):
    """
    记录函数过程的状态，是经过merger处理过的状态
    """
    not_found_in_cache = -4
    unknown = -3
    record_incomplete = -2
    not_started_yet = -1
    running = 0
    finished = 1
    failed = 2
    partially_finished = 3
    process_shutdown = 4

    @staticmethod
    def is_dead(state: enum.Enum):
        dead = state.value in {-4, -1, 1, 2, 3, 4}
        return dead


class CallCategory(enum.Enum):
    root = -1
    normal = 0
    # loop = 1
    cross_thread = 2
    cross_process = 3
    # branch = 4