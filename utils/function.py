#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 定义一些公用的函数
import re

# 去除内容中的注释内容
def trimAnnotation(content):
    content = content.strip()
    content = re.compile(r"\s/\*.*?\*/", re.S).sub("", content)
    content = re.compile(r"//.*").sub("", content)

    return content

# 去除单引号和双引号中的内容
def trimQuoteStr(content):
    content = content.replace("\\'", "").replace('\\"', "")
    return re.compile(r"('.*?'|\".*?\")").sub("", content)

'''
从当前文件内容中找到对应的函数定义
func_name: 函数名
content: 函数所在文件内容
'''
def findFuncByContent(func_name, content):
    funcs = []
    regex = r'''(\s*(public|protected|private)\s+(static\s+)?function\s+{}.*?)\s+((public|protected|private)\s+function|$)'''.format(func_name)
    for t in re.compile(regex, re.I | re.S).findall(content):
        funcs.append(trimAnnotation(t[0]))
    return funcs

'''
从当前文件内容中找到关键字对应的函数定义
keyword: 待查找的关键字
content: 函数所在文件内容
'''
def findFuncByKeyword(keyword, content):
    funcs = []
    regex = r'''(\s*(public|protected|private)\s*(static)?\s+function\s+.*?{}.*?)\s+((public|protected|private)\s+function|$)'''.format(re.escape(keyword))
    for t in re.compile(regex, re.I | re.S).findall(content):
        funcs.append(trimAnnotation(t[0]))
    return funcs

def findClassByContent(class_name, content):
    if class_name == getClassname(content):
        return True
    return False


'''
解析函数中全部的其他函数调用
func: 函数内容主题
content: 函数所在文件内容
'''
def analyFunc(func, content, rnt={"self_class_func": [], "other_class_func":[]}, is_init=True):
    if is_init:
        rnt = {"self_class_func": [], "other_class_func":[]}
    for func_name in re.compile(r"\$this\s*\->\s*(\w+)\(", re.I | re.S).findall(func):
        if func_name not in rnt['self_class_func']:
            rnt['self_class_func'].append(func_name)
            for func_content in findFuncByContent(func_name, content):
                analyFunc(func_content, content, rnt, False)
    for t in re.compile(r"\$this\s*\->\s*\w+\s*->\s*(\w+)\(", re.I | re.S).findall(func):
        rnt['other_class_func'].append(t) if t not in rnt['other_class_func'] else None
    return rnt

# 获取当前类的类型
def getClassname(content):
    class_name = ""
    for t in re.compile(r"class\s+(\w+)\s*(?:extends|{)", re.I | re.S).findall(content):
        class_name = t
        break
    return class_name

# 获取当前类的父类的类名
def getParentClassname(content):
    class_name = ""
    for t in re.compile(r"class\s+\w+\s*extends\s*(\w+)\s*{", re.I | re.S).findall(content):
        class_name = t
        break
    return class_name

def convertList(data):
    if isinstance(data,list):
        return data
    else:
        return [data, ]



if __name__ == '__main__':
    filepath = "D:/phpstudy_pro/WWW/CodeIgniter4/system/ThirdParty/Kint/Parser/ProxyPlugin.php"
    with open(filepath, 'rb')  as h:
        content = h.read()
        parser = parsePHPFile(content, filepath)
        print(parser['ProxyPlugin']['funcs']['parse'])