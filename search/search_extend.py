#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 找到一些可扩展的函数
# PHP中扩展函数主要是魔术方法__toString(), __call(), __invoke(), __get(), __set()

from utils.function import findFuncByContent

def search_extend(content):
	extend_funcs = {}
	extend_funcnames = ["__toString", "__call", "__invoke", "__get", "__set"]

	for funcname in extend_funcnames:
		for func in findFuncByContent(funcname, content):
			extend_funcs[funcname] = func
	return extend_funcs