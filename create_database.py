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
    app.root_path, 'my_ha_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


# 创建数据库模型
# 棉铃虫信息 表
class Ha_info(db.Model):  # 表名将会是 ha_info
    id = db.Column(db.Integer, primary_key=True)  # 主键
    x1 = db.Column(db.Float)  # 一代幼虫量(头／百株)
    x2 = db.Column(db.Float)  # 二代幼虫量(头／百株)
    y = db.Column(db.Float)  # 理论产量损失率(%)
    date = db.Column(db.DateTime)  # 记录时间
    id_user = db.Column(db.Integer,
                        db.ForeignKey('user_info.id_user'))  # 外键，记录农户id
    id_area = db.Column(db.Integer,
                        db.ForeignKey('area_info.id_area'))  # 外键，记录地区id


# 农户 表
class User_info(db.Model):  # 表名将会是 user_info （自动生成，小写处理）
    id_user = db.Column(db.Integer, primary_key=True)  # 主键，农户id
    name_user = db.Column(db.String(20))  # 农户称呼
    pwd_user = db.Column(db.String())  # 农户密码
    id_area = db.Column(db.Integer,
                        db.ForeignKey('area_info.id_area'))  # 外键，农户所属地区id


# 地区 表
class Area_info(db.Model):  # 表名将会是 area_info （自动生成，小写处理）
    id_area = db.Column(db.Integer, primary_key=True)  # 主键，地区id
    name_area = db.Column(db.String(20))  # 地区名
    id_admin = db.Column(db.Integer,
                         db.ForeignKey('admin_info.id_admin'))  # 外键，管理员id


# 管理员 表
class Admin_info(db.Model):  # 表名将会是 user_info （自动生成，小写处理）
    id_admin = db.Column(db.Integer, primary_key=True)  # 主键，管理员id
    name_admin = db.Column(db.String(20))  # 管理员称呼
    pwd_admin = db.Column(db.String())  # 管理员密码


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
    name_user = '蔡雨豪'
    list_ha = [
        {'x1': '50', 'x2': '300', 'y': '25.624243', 'date': '2022-01-29', },
        {'x1': '10', 'x2': '60', 'y': '15.435247', 'date': '2022-01-25', },
        {'x1': '20', 'x2': '120', 'y': '17.6739028', 'date': '2022-01-26', },
        {'x1': '30', 'x2': '180', 'y': '20.1182874', 'date': '2022-01-27', },
        {'x1': '40', 'x2': '250', 'y': '22.768400800000002', 'date': '2022-01-28', },
    ]
    user = User(name=name)  # 把 name = '蔡雨豪' 传给 User 模型中的 name
    db.session.add(user)
    for h in Helicoverpa_armigeras:
        ha = Helicoverpa_armigera(X1=h['X1'],
                                  X2=h['X2'])  # 创建一个 Helicoverpa_armigera 记录
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

if __name__ == "__main__":
    app.run(debug=True)