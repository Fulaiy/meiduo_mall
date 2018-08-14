#!/usr/bin/env python

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_index_html.py
"""
import sys
sys.path.insert(0, '../')
# 因为generate_static_index_html执行要进行数据库查询，所以要把项目的配置文件导入
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

 # 让django进行初始化设置
import django
django.setup()

# 先加载路径 在导包
from contents.crons import generate_static_index_html


if __name__ == '__main__':
    generate_static_index_html()