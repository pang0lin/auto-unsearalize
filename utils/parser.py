#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 解析PHP文件
import re
from utils.function import trimAnnotation,trimQuoteStr

# 解析PHP文件，解析对应的类名称，函数名称
def parsePHPFile(file, path):
    rnt = {}
    file = trimAnnotation(file) #去除注释内容，避免干扰
    lines = file.split("\n")
    for line in lines:
        line = trimQuoteStr(line) #去除单双引号中的内容，避免干扰
        class_name = isClassDefine(line)
        if class_name:
            rnt[class_name] = {"funcs":{}, "left_count":0, "right_count": 0, "over": False}
        left_count, right_count = parseLine(line)

        #开始计算类的开始和结束
        for tmp_class_name in rnt:
            if not rnt[tmp_class_name].get("over"):
                rnt[tmp_class_name]["left_count"]   += left_count
                rnt[tmp_class_name]["right_count"]  += right_count
                if rnt[tmp_class_name]["left_count"] > 0 and rnt[tmp_class_name]["right_count"] > 0 and rnt[tmp_class_name]["left_count"] == rnt[tmp_class_name]["right_count"]:
                    rnt[tmp_class_name]["over"] = True

        unover_classname = getUnoverClass(rnt)
        if not unover_classname:
            continue
        function_name = isFunctionDefine(line)
        if function_name:
            rnt[unover_classname]["funcs"][function_name] = {"code":"", "left_count":0, "right_count":0, "over":False}
        #开始计算函数的开始和结束
        for tmp_function_name in rnt[unover_classname]['funcs']:
            if not rnt[unover_classname]['funcs'][tmp_function_name].get("over"):
                rnt[unover_classname]['funcs'][tmp_function_name]["left_count"]     += left_count
                rnt[unover_classname]['funcs'][tmp_function_name]["right_count"]    += right_count
                if rnt[unover_classname]['funcs'][tmp_function_name]["left_count"] > 0 and rnt[unover_classname]['funcs'][tmp_function_name]["right_count"] > 0 and rnt[unover_classname]['funcs'][tmp_function_name]["right_count"] == rnt[unover_classname]['funcs'][tmp_function_name]["left_count"]:
                    rnt[unover_classname]['funcs'][tmp_function_name]["over"] = True
                rnt[unover_classname]['funcs'][tmp_function_name]["code"] += line + "\n"
                        

    for tmp_class_name in rnt:
        if rnt[tmp_class_name]["left_count"] != rnt[tmp_class_name]["right_count"]:
            print("Parse Class {} Error: {}".format(tmp_class_name, path))
        for tmp_func_name in rnt[tmp_class_name]["funcs"]:
            if rnt[tmp_class_name]["funcs"][tmp_func_name]["left_count"] != rnt[tmp_class_name]["funcs"][tmp_func_name]["right_count"]:
                print("Parse Class {} Function {} Error: {}".format(tmp_class_name, tmp_func_name, path, ))
    return rnt


def getUnoverClass(result):
    for class_name in result:
        if result[class_name].get("over") == False:
            return class_name
    return False

def getUnoverFunction(result):
    for class_name in result:
        if result[class_name].get("over") == False:
            return class_name
    return False

#解析每一行中的左右花括号
def parseLine(line):
    return line.count("{"), line.count("}")

# 判断本行是否为类定义语句
def isClassDefine(line):
    line = line.strip()
    for t in re.compile(r"^(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+\w+)?(?:{|$)").findall(line):
        return t
    return False

# 判断本行是否为函数定义语句
def isFunctionDefine(line):
    line = line.strip()
    for t in re.compile(r"^(?:public|protected|private)\s+(?:static\s*)?function\s+(\w+)\(").findall(line):
        return t
    return False

if __name__ == '__main__':
    with open('D:/phpstudy_pro/WWW/CodeIgniter4/system/ThirdParty/Kint/Renderer/Renderer.php', 'rb') as h:
        parsePHPFile(h.read())