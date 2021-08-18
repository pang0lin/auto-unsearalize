#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 输出保存结果数据
import sys,time
from utils.function import analyFunc
from utils.parser   import parsePHPFile
'''
 <tr>
    <td class=start>王艳艳</td>
    <td class=start>&nbsp;</td>
    <td class=start>&nbsp;</td>
    <td class=start>&nbsp;</td>
    <td class=start>&nbsp;</td>
</tr>

<tr>
    <td class=end>王艳艳</td>
    <td class=end>&nbsp;</td>
    <td class=end>&nbsp;</td>
    <td class=end>&nbsp;</td>
    <td class=end>&nbsp;</td>
</tr>
'''
def saveChain(chains, number=1):
    start_chain_html = ''
    end_chain_html = ''
    for chain in chains:
        if not isinstance(chain["filepath"],list):
            chain["filepath"] = [chain["filepath"], ]

        clearChain(chain)
        if chain['flag'] == -1:
            start_chain_html += '''
                <tr>
                    <td class=start>{}</td>
                    <td class=start>{}</td>
                    <td class=start>{}</td>
                    <td class=start>{}</td>
                    <td class=start>{}</td>
                </tr>
            '''.format("入口", chain['func_name'], "<br>".join(chain['filepath']), chain['from'], chain['depth'])
        if chain['flag'] == 1:
            end_chain_html += '''
                <tr>
                    <td class=end>{}</td>
                    <td class=end>{}</td>
                    <td class=end>{}</td>
                    <td class=end>{}</td>
                    <td class=end>{}</td>
                </tr>
            '''.format("出口", chain['func_name'], "<br>".join(chain['filepath']), chain['from'], chain['depth'])
        chain = None

    with open("html/chain.tpl.html", "rb") as h:
        content = h.read()
        content = content.replace("{start_chain_html}", start_chain_html).replace("{end_chain_html}", end_chain_html).replace('{now_time}', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())).replace("{sequence}", str(number))
        with open("output/result-{}.html".format(number), "wb") as w:
            w.write(content)

# 排除chain中的干扰数据，一个函数来源于多个文件，但是只有某一个文件中的函数包含了from方法
def clearChain(chain):

    #正向清理
    if chain['flag'] == -1:
        for filepath in chain['filepath']:
            with open(filepath, 'rb') as h:
                file_content = h.read()
                parser = parsePHPFile(file_content, filepath)
                for class_name in parser.keys():
                    if chain['from'] in parser[class_name]['funcs'].keys():
                        function_usages = analyFunc(parser[class_name]['funcs'][chain['from']]['code'], file_content)
                        if chain['func_name'] not in function_usages['other_class_func'] and chain['func_name'] not in parser[class_name]['funcs'][chain['from']]['code']:
                            chain['filepath'].remove(filepath)
    #反向清理
    else:
        for filepath in chain['filepath']:
            with open(filepath, 'rb') as h:
                file_content = h.read()
                parser = parsePHPFile(file_content, filepath)
                for class_name in parser.keys():
                    if chain['func_name'] in parser[class_name]['funcs'].keys():
                        function_usages = analyFunc(parser[class_name]['funcs'][chain['func_name']]['code'], file_content)
                        if chain['from'] not in function_usages['other_class_func'] and chain['from'] not in parser[class_name]['funcs'][chain['func_name']]['code']:
                            chain['filepath'].remove(filepath)
