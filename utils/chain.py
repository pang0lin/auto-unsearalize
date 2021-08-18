#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 调用链相关的函数

from utils.parser   import parsePHPFile
from utils.function import analyFunc, convertList


# 往后扩展外部函数调用
# files: 当前全部的文件信息
# chain_functions: 当前已知链中的函数
def extendChainNext(files, chain_functions, depth):
    chain_function_names = getChainList(chain_functions)
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for class_name in parser.keys():
            for func_name in parser[class_name]['funcs']:
                #当前的函数在已知不安全的函数列表中
                if func_name in chain_function_names:
                    func_code = parser[class_name]['funcs'][func_name]['code']
                    function_usages = analyFunc(func_code, files[filepath])
                    for other_class_func in function_usages['other_class_func']:
                        addChainNext(chain_functions, {"func_name":other_class_func, "filepath":filepath, "depth": depth+1, "from":func_name})

    return chain_functions

# 往前扩展外部函数调用
# files: 当前全部的文件信息
# chain_functions: 当前已知链中的函数
def extendChainPrev(files, chain_functions, depth):
    chain_function_names = getChainList(chain_functions)
    for filepath in files:
        parser = parsePHPFile(files[filepath], filepath)
        for class_name in parser.keys():
            for func_name in parser[class_name]['funcs']:
                func_code = parser[class_name]['funcs'][func_name]['code']
                function_usages = analyFunc(func_code, files[filepath])
                for chain_function_name in chain_function_names:
                    #如果当前某个函数在另一个函数的外部调用里面
                    if chain_function_name in function_usages['other_class_func']:
                        addChainPrev(chain_functions, {"func_name":func_name, "filepath":filepath, "depth": depth+1, "from":chain_function_name})
    return chain_functions

def getChainList(chain_functions):
    rnt = []
    for chain_function in chain_functions:
        rnt.append(chain_function['func_name'])
    return rnt

def addChainNext(current_chains, new_chain):
    current_chain_list = getChainList(current_chains)
    if new_chain['func_name'] not in current_chain_list:
        current_chains.append(new_chain)
    else:
        for chain in current_chains:
            if chain["from"] == new_chain['from']:
                if isinstance(chain["filepath"],list):
                    if new_chain['filepath'] not in chain['filepath']:
                        chain['filepath'].append(new_chain['filepath'])
                else:
                    if chain['filepath'] == new_chain['filepath']:
                        chain['filepath'] = [chain['filepath'], ]
                    else:
                        chain['filepath'] = [chain['filepath'], new_chain['filepath'], ]
    return current_chains
    
def addChainPrev(current_chains, new_chain):
    current_chain_list = getChainList(current_chains)
    if new_chain['func_name'] not in current_chain_list:
        current_chains.append(new_chain)
    else:
        for chain in current_chains:
            if chain["func_name"] == new_chain['func_name']:
                if isinstance(chain["filepath"],list):
                    if new_chain['filepath'] not in chain['filepath']:
                        chain['filepath'].append(new_chain['filepath'])
                else:
                    if chain['filepath'] == new_chain['filepath']:
                        chain['filepath'] = [chain['filepath'], ]
                    else:
                        chain['filepath'] = [chain['filepath'], new_chain['filepath'], ]

    return current_chains

def addChainFinal(current_chains, new_chain):
    flag = True
    #如果新的chain已经存在，则直接不要new_chain
    if new_chain in current_chains:
        return current_chains
    for chains in current_chains:
        #如果调用链中的函数完全相同，则只需要更新filepath即可
        chain_list      = getChainList(chains)
        new_chain_list  = getChainList(new_chain)
        if chain_list == new_chain_list:
            flag = False
            for i in range(len(chains)):
                c_chain_filepath = convertList(chains[i]['filepath'])
                n_chain_filepath = convertList(new_chain[i]['filepath'])
                # print(type(c_chain_filepath), type(n_chain_filepath))
                chains[i]['filepath'] = list(set(c_chain_filepath + n_chain_filepath))

    if flag: current_chains.append(new_chain)

    return current_chains


def printChain(chains):
    for chain in chains:
        print chain['func_name'],
    print('\n')

def findPreChain(chains, chain, flag, is_init, rnt=[]):
    if is_init: rnt = []
    rnt.append({"func_name":chain['func_name'], "filepath":chain['filepath'], "flag":flag, "from":chain['from'], "depth":chain['depth']})
    for tmp_chain in chains:
        if tmp_chain['func_name'] == chain['from']:
            findPreChain(chains, tmp_chain, flag, False, rnt)
    return rnt

# 对比开始链和结束链，看两条链是否有交集
def compareChain(start_chains, end_chains):
    rnt = []
    for start_chain in start_chains:
        for end_chain in end_chains:
            if start_chain['func_name'] == end_chain['func_name'] and start_chain['func_name'] not in ['__destruct', '__wakeup', ]:
                tmp_chain = []
                tmp_chain += findPreChain(start_chains, start_chain, -1, True)
                tmp_chain += findPreChain(end_chains, end_chain, 1, True)
                rnt.append(tmp_chain)
                print('    [-] Find chain, key function: ' + start_chain['func_name'])
    return rnt
                