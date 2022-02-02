import os
import sys
import app

from flask import Flask

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)

# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址：
SQLALCHEMY_DATABASE_URI_1 = prefix + os.path.join(
    app.root_path, os.getenv('DATABASE_FILE', 'my_ha_data.db'))
print("线下可用结果：" + SQLALCHEMY_DATABASE_URI_1)  # 线下可用

SQLALCHEMY_DATABASE_URI_2 = prefix + os.path.join(
    os.path.dirname(app.root_path), os.getenv('myha\my_ha_data.db', 'my_ha_data.db'))
print("线下不可结果：" + SQLALCHEMY_DATABASE_URI_2)  # 线下不可用
"""
输出：
线下可用结果：sqlite:///e:\手机又没电了的云文档\001-本科生\004-辅修\005-Python_MySQL大作业\program0-2022-01-10\myha\my_ha_data.db
线下不可结果：sqlite:///e:\手机又没电了的云文档\001-本科生\004-辅修\005-Python_MySQL大作业\program0-2022-01-10\my_ha_data.db
"""


app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_1  # 线下不能运行，希望线上能好
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
#     os.path.dirname(app.root_path), os.getenv(
#         'DATABASE_FILE', 'my_ha_data.db'))  # 这个一用就找不到数据库的位置