#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : interfaces.py
# @Time      : 2021/4/16 14:34
# @Author    : Lee

from abc import ABC, abstractmethod

from typing import List, Tuple, Union

from jiliang_process.process_monitor_types import ProcessState



class StatusRecordInterface(ABC):
    pass


class StatusNodeInterface(ABC):
    pass


class GraphBlockInterface(ABC):
    pass


class StatusMergerInterface(ABC):
    @abstractmethod
    def merge_info(self, records: List[StatusRecordInterface]) -> Tuple[List[str], List[str]]:
        info = []
        err = []
        return info, err

    @abstractmethod
    def merge_status(self, records: List[StatusRecordInterface]) -> Tuple[ProcessState, List[str], List[str],
                                                                          List[float], str]:
        '''
        Because original status records are generated when events of interests occur, so a task may have more than one
        record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
        :param records: related records
        :return: ProcessState
        '''
        return ProcessState.finished, [], [], [],""

    @staticmethod
    @abstractmethod
    def build_graph_node(x: Union[StatusNodeInterface, None]) -> GraphBlockInterface:
        block = GraphBlockInterface()
        return block
