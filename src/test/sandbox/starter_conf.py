#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : starter_conf.py
# @Time      : 2021/3/24 10:01
# @Author    : Lee

import configparser,os


class StarterConf:
    def __init__(self):
        self.config = configparser.ConfigParser()
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path,"start_conf.ini")
        self.config.read(file, encoding='UTF-8')

    def __get_section(self, section_name):
        res = self.config._sections.get(section_name)
        return res

    def get_to_deco(self):
        modules_to_deco = {}
        to_deco = self.__get_section("to_deco")
        for k in to_deco:
            tokens = k.strip().split(".")
            module_name = tokens[0]
            rest = ".".join(tokens[1:])
            if module_name not in modules_to_deco:
                modules_to_deco[module_name] = [(rest,to_deco[k])]
            else:
                modules_to_deco[module_name].append((rest, to_deco[k]))
        return modules_to_deco



_starter_conf = StarterConf()


