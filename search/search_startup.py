#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 找到所有反序列化的入口点函数
# PHP中反序列化直接的入口点只有__destruct和__wakeup

# from utils.function import findFuncByContent

# def search_startup(files):
# 	start_funcs = {}
# 	start_funcnames = ["__destruct", "__wakeup"]

# 	for filepath in files:
# 		for funcname in start_funcnames:
# 			for func in findFuncByContent(funcname, files[filepath]):
# 				start_funcs[filepath] = func
# 	return start_funcs

import re
import sys
from utils.function import findFuncByKeyword
from utils.parser   import parsePHPFile

def search_startup(files):
    rnt = []
    exec_regex = [
        r"(?:__destruct|__wakeup)\(",
    ]
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for regex in exec_regex:
            for class_name in parser.keys():
                for func_name in parser[class_name]["funcs"]:
                    for t in re.compile(regex, re.I).findall(parser[class_name]["funcs"][func_name]["code"]):
                        rnt.append({"filepath":filepath, "func_name":func_name, "code":parser[class_name]["funcs"][func_name]["code"], "from":t})
    return rnt
