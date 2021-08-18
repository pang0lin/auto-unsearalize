#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 找到反序列化的出口点，所有的反序列化最理想的出口应该是命令执行

import re
import sys
from utils.function import findFuncByKeyword
from utils.parser   import parsePHPFile

#按照命令执行对出口函数进行匹配
def search_execfuncs(files):
    rnt = []
    exec_regex = [
        r"\W(?:call_user_func_array|call_user_func)\(",
        r"\W(?:eval|assert)\s*\(",
        r"\W\$\w+\->\$?\w+\([\w$_, '\"]*?\$\w+\->"
    ]
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for regex in exec_regex:
            for class_name in parser.keys():
                for func_name in parser[class_name]["funcs"]:
                    for t in re.compile(regex, re.I).findall(parser[class_name]["funcs"][func_name]["code"]):
                        rnt.append({"filepath":filepath, "func_name":func_name, "code":parser[class_name]["funcs"][func_name]["code"], "from":t})
    return rnt

#按照SQL操作对出口函数进行匹配
def search_sqlfuncs(files):
    rnt = []
    sqli_regex = [
        r"\W(?:mysql_query|mysqli_query)\(",
        r"\W(?:prepare|execute)\(", #预编译的SQL语句执行
    ]
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for regex in sqli_regex:
            for class_name in parser.keys():
                for func_name in parser[class_name]["funcs"]:
                    for t in re.compile(regex, re.I).findall(parser[class_name]["funcs"][func_name]["code"]):
                        rnt.append({"filepath":filepath, "func_name":func_name, "code":parser[class_name]["funcs"][func_name]["code"], "from":t})
    return rnt

#按照任意文件上传/下载/删除对出口函数进行匹配
def search_filefuncs(files):
    rnt = []
    file_regex = [
        r"\W(?:move_uploaded_file|file_put_contents)\(",
        r"\W(?:copy|unlink)\(", 
    ]
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for regex in file_regex:
            for class_name in parser.keys():
                for func_name in parser[class_name]["funcs"]:
                    for t in re.compile(regex, re.I).findall(parser[class_name]["funcs"][func_name]["code"]):
                        rnt.append({"filepath":filepath, "func_name":func_name, "code":parser[class_name]["funcs"][func_name]["code"], "from":t})
    return rnt

#按照XXE漏洞对出口函数进行匹配
def search_xxefuncs(files):
    rnt = []
    xxe_regex = [
        r"\W(?:simplexml_load_string|xml_parse)\(",
    ]
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for regex in xxe_regex:
            for class_name in parser.keys():
                for func_name in parser[class_name]["funcs"]:
                    for t in re.compile(regex, re.I).findall(parser[class_name]["funcs"][func_name]["code"]):
                        rnt.append({"filepath":filepath, "func_name":func_name, "code":parser[class_name]["funcs"][func_name]["code"], "from":t})
    return rnt


def search_endup(files):
    return search_execfuncs(files)  + search_sqlfuncs(files) + search_filefuncs(files) + search_xxefuncs(files)