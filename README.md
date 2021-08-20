# 工具介绍
自动化反序列化调用链发现工具，目前仅支持PHP语言，JAVA版本后面再补

# 反序列化介绍
反序列化是目前比较流行的一种漏洞，通常是由于在反序列化的中可以自动执行一些函数，例如PHP反序列化时会自动执行__destruct函数，JAVA反序列化时会自动执行readObject函数。通过在自动执行的函数中寻找敏感的操作，就可能导致诸如命令执行之类的漏洞。
反序列化最核心的点在于寻找利用链，这里还是以PHP来说明整个利用链的过程
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/master/imgs/3.png "反序列化调用链图")
此工具主要是先找到反序列化中的入口与出口函数，通过入口函数向下查找函数调用，通过出口函数向上查找函数调用

# 工具使用
```
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     project dir, D:/wamp/www/
  -D DEPTH, --depth=DEPTH
                        search depth, eg 5
```
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/master/imgs/1.png "使用过程截图")

![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/master/imgs/2.png "查看结果截图")



