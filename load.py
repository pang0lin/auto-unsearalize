#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 把所有的文件都加载到内存中，方便以后进行正则匹配的工作
import os

def listdir(path, list_name):  
    for file in os.listdir(path):  
        file_path = os.path.join(path, file).replace("\\", "/")
        if os.path.isdir(file_path):  
            listdir(file_path, list_name)
        elif os.path.splitext(file_path)[1] == '.php' and file_path not in list_name:  
            list_name.append(file_path)
    return list_name


def load_dir(file_dir):
    memory_files = {}
    for file in listdir(file_dir, []):
        with open(file, 'rb') as h:
            memory_files[file] = h.read()
    return memory_files

if __name__ == '__main__':
    print(load_dir("D:/phpstudy_pro/WWW/CodeIgniter4/"))