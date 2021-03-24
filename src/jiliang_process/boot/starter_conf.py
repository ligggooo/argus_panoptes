#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : starter_conf.py
# @Time      : 2021/3/24 10:01
# @Author    : Lee

import configparser, os


class MyConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def optionxform(self, optionstr):
        return optionstr

class StarterConf:
    def __init__(self):
        self.config = MyConfigParser()
        path = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(path,"start_conf.ini")
        self.config.read(file, encoding='UTF-8')
        self.deco_dict = {}

    def __get_section(self, section_name):
        res = self.config._sections.get(section_name)
        return res

    def get_to_deco(self):
        modules_to_deco = {}
        to_deco = self.__get_section("to_deco")
        for k in to_deco:
            tokens = k.strip().split("@")
            module_name = tokens[0]
            rest = tokens[1]
            if module_name not in modules_to_deco:
                modules_to_deco[module_name] = [(rest,to_deco[k])]
            else:
                modules_to_deco[module_name].append((rest, to_deco[k]))
        self.deco_dict = modules_to_deco


    def __seg_match(self,long_name,short_name):
        """
        name 用点号隔开，shortname全段匹配上才算匹配上
        :param long_name:
        :param short_name:
        :return:
        """
        long_tokens = long_name.split(".")
        short_tokens = short_name.split(".")
        L = len(long_tokens)-1
        l = len(short_tokens)-1
        for i in range(l+1):
            if long_tokens[L-i] != short_tokens[l-i]:
                return False
        return True

    def match(self, module_name):
        for name in self.deco_dict:
            if self.__seg_match(name, module_name):
                return self.deco_dict.get(name)
        return None


def get_starter_conf():
    _starter_conf = StarterConf()
    _starter_conf.get_to_deco()
    return _starter_conf


