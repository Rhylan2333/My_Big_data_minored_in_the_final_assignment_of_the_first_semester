import os
import sys

import click
from flask import Flask, escape, render_template, url_for
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类。Flask-SQLAlchemy 版本 2.4.0 Apr 25, 2019 可行

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)

# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址：
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
    app.root_path, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    pwd = db.Column(db.String())  # 密码


class Helicoverpa_armigera(db.Model):  # 表名将会是 helicoverpa_armigera
    id = db.Column(db.Integer, primary_key=True)  # 主键
    X1 = db.Column(db.Float)  # 一代幼虫量(头／百株)
    X2 = db.Column(db.Float)  # 二代幼虫量(头／百株)
    date = db.Column(db.DateTime)


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = '蔡雨豪'
    Helicoverpa_armigeras = [{
        'X1': '123',
        'X2': '233',
        'date': ''
    }, {
        'X1': '135',
        'X2': '466',
        'date': ''
    }]
    user = User(name=name)  # 把 name = '蔡雨豪' 传给 User 模型中的 name
    db.session.add(user)
    for h in Helicoverpa_armigeras:
        ha = Helicoverpa_armigera(X1=h['X1'], X2=h['X2']) # 创建一个 Helicoverpa_armigera 记录
        db.session.add(ha)

    db.session.commit()
    click.echo('虚拟数据已写入数据库 mydatabase。')


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """使用 --drop 选项可以删除表后重新创建"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
        print("数据库已清空。")
    db.create_all()
    click.echo('数据库已初始化。')  # 输出提示信息


@app.route('/') 
def index():
    """为了让模板正确渲染，我们还要把模板内部使用的变量通过关键字参数传入这个函数"""
    """左边的 movies 是模板 index.html 中使用的变量名称，右边的 movies 则是该变量指向 app.py 中的实际对象"""
    user = User.query.first()  # 读取用户记录
    ha = Helicoverpa_armigera.query.all()  # 读取所有棉铃虫记录
    return render_template('index0.html', user=user, ha=ha)
