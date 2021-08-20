#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from optparse import OptionParser 
from load import load_dir
from search.search_startup  import search_startup
from search.search_extend   import search_extend
from search.search_endup    import search_endup
from utils.parser           import parsePHPFile
from utils.html             import saveChain
from utils.function         import *
from utils.chain            import *


if __name__ == '__main__':
    parser = OptionParser() 
    parser.add_option("-d", "--dir", action="store", 
                    dest="dir", 
                    help="project dir, D:/wamp/www/") 
    parser.add_option("-D", "--depth", action="store", 
                    dest="depth", 
                    default= "5",
                    help="search depth, eg 5") 

    (options, args) = parser.parse_args() 

    if not options.dir or not options.depth:
        print("usage: python main.py --dir=D:/wamp/www --depth=5")
        sys.exit()

    base_dir = options.dir
    number = 1

    print("[*] Start to load all file in memory...")
    # 把全部文件相关信息保存到内存
    files = load_dir(base_dir)
    if not files:
        print("[$] Dir is empty.")
        sys.exit()

    print("[*] File load success.")
    depth = int(options.depth)

    # 找到反序列化的入口函数
    print("[*] Start to search unserialize start functions...")
    startup_functions = search_startup(files)
    if not startup_functions:
        print("[$] Couldn't find any unserialize start function.")
        sys.exit()
    print("[*] Found unserialize start function. success")

    #找到反序列化的出口函数
    print("[*] Start to search unserialize end functions...")
    endup_functions = search_endup(files)
    if not endup_functions:
        print("[$] Couldn't find any unserialize end function.")
        sys.exit()
    print("[*] Found unserialize end function. success")
    #从入口位置开始查找，扩展入口depth层
    start_chain_funs = [] 
    for func in startup_functions:
        start_chain_funs = addChainNext(start_chain_funs, {"func_name": func['func_name'], "filepath":func['filepath'], "depth":0, "from": func['from']})

    #从出口位置开始查找，扩展出口depth层
    end_chain_funs = []
    for func in endup_functions:
        end_chain_funs = addChainPrev(end_chain_funs, {"func_name": func['func_name'], "filepath":func['filepath'], "depth":0, "from": func['from']})

    #保存全部的反序列化链
    final_chains = []
    print("[*] Start find the unserialize chain ...")
    for i  in range(depth):
        print("  [*] search chain depth {},started ".format(i))
        start_chain_funs = extendChainNext(files, start_chain_funs, i)

        # printChain(start_chain_funs)
        end_chain_funs = extendChainPrev(files, end_chain_funs, i)

        for new_chain in compareChain(start_chain_funs, end_chain_funs):
            final_chains = addChainFinal(final_chains, new_chain)

    print("[*] Total chain {}, Start to output the result...".format(len(final_chains)))
    for chains in final_chains:
        saveChain(chains, number)
        number += 1

    print('over,see the result in /output/result-*.html')
