import os
import sys
from datetime import date, datetime
from email.policy import default
from enum import unique

import click
from flask import Flask, escape, render_template, request, url_for
from flask_sqlalchemy import \
    SQLAlchemy  # 导入扩展类。Flask-SQLAlchemy 版本 2.4.0 Apr 25, 2019 可行

import formula

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
"""
# 接下来创建数据库模型。
    模型类要声明继承 db.Model。
    每一个类属性（字段）要实例化 db.Column，传入的参数为字段的类型。
    在 db.Column() 中添加额外的选项（参数）可以对字段进行设置。比如，primary_key 设置当前字段是否为主键。除此之外，常用的选项还有 nullable（布尔值，是否允许为空值）、index（布尔值，是否设置索引）、unique（布尔值，是否允许重复值）、default（设置默认值）等。
"""


# 棉铃虫信息 表
class Ha_info(db.Model):  # 表名将会是 ha_info
    id_ha = db.Column(db.Integer, primary_key=True)  # 主键
    x1 = db.Column(db.Float)  # 一代幼虫量(头／百株)
    x2 = db.Column(db.Float)  # 二代幼虫量(头／百株)
    y = db.Column(db.Float)  # 理论产量损失率(%)
    date = db.Column(db.Date, default=date.today())  # 记录时间
    id_user = db.Column(db.Integer,
                        db.ForeignKey('user_info.id_user'))  # 外键，记录农户id
    id_area = db.Column(db.Integer,
                        db.ForeignKey('area_info.id_area'))  # 外键，记录地区id


# 农户 表
class User_info(db.Model):  # 表名将会是 user_info （自动生成，小写处理）
    id_user = db.Column(db.Integer, primary_key=True)  # 主键，农户id
    name_user = db.Column(db.String(20), unique=True)  # 农户称呼
    pwd_user = db.Column(db.String())  # 农户密码
    id_area = db.Column(db.Integer,
                        db.ForeignKey('area_info.id_area'))  # 外键，农户所属地区id


# 地区 表
class Area_info(db.Model):  # 表名将会是 area_info （自动生成，小写处理）
    id_area = db.Column(db.Integer, primary_key=True)  # 主键，地区id
    name_area = db.Column(db.String(20), unique=True)  # 地区名
    id_admin = db.Column(db.Integer,
                         db.ForeignKey('admin_info.id_admin'))  # 外键，管理员id


# 管理员 表
class Admin_info(db.Model):  # 表名将会是 user_info （自动生成，小写处理）
    id_admin = db.Column(db.Integer, primary_key=True)  # 主键，管理员id
    name_admin = db.Column(db.String(20), unique=True)  # 管理员称呼
    pwd_admin = db.Column(db.String())  # 管理员密码


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """默认情况下，函数名称就是命令的名字，现在执行 flask initdb 命令就可以创建数据库表："""
    """使用 --drop 选项可以删除表后重新创建"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
        print("数据库已清空。")
    db.create_all()
    click.echo('数据库已初始化。')  # 输出提示信息


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name_user = '蔡雨豪'
    list_ha = [
        {
            'x1': '50',
            'x2': '300',
            'y': '25.624243',
            'date': date(2022, 1, 29),
        },
        {
            'x1': '10',
            'x2': '60',
            'y': '15.435247',
            'date': date(2022, 1, 25),
        },
        {
            'x1': '20',
            'x2': '120',
            'y': '17.6739028',
            'date': date(2022, 1, 26),
        },
        {
            'x1': '30',
            'x2': '180',
            'y': '20.1182874',
            'date': date(2022, 1, 27),
        },
        {
            'x1': '40',
            'x2': '250',
            'y': '22.768400800000002',
            'date': date(2022, 1, 28),
        },
    ]
    user = User_info(
        name_user=name_user
    )  # 把这个 def 中的 name_user = '蔡雨豪' 左传给 User_info 模型中的 name_user
    db.session.add(user)
    for row_ha in list_ha:
        print(row_ha)
        ha = Ha_info(
            x1=row_ha['x1'],
            x2=row_ha['x2'],
            y=row_ha['y'],
            date=row_ha['date']
        )  # 创建一个 row_ha 记录，等号左边的“x1、x2、y”与ha_info表中的“x1、x2、y”要匹配/相等
        db.session.add(ha)

    db.session.commit()
    db.session.close()
    click.echo('虚拟数据已写入数据库 my_ha_data。')


@app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == "POST":
#         X1 = eval(request.form.get('left')) / 50
#         X2 = eval(request.form.get('right')) / 300
#         Y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(X1, X2)
#         return render_template('index.html', RESULT=str(Y0))
#     return render_template('index.html')
# 返回渲染好的模板作为响应
def show_list_ha():
    # 定义虚拟数据
    name_user = '蔡雨豪'
    list_ha = [
        {
            'x1': '50',
            'x2': '300',
            'y': '25.624243',
            'date': '2022-01-29',
        },
        {
            'x1': '10',
            'x2': '60',
            'y': '15.435247',
            'date': '2022-01-25',
        },
        {
            'x1': '20',
            'x2': '120',
            'y': '17.6739028',
            'date': '2022-01-26',
        },
        {
            'x1': '30',
            'x2': '180',
            'y': '20.1182874',
            'date': '2022-01-27',
        },
        {
            'x1': '40',
            'x2': '250',
            'y': '22.768400800000002',
            'date': '2022-01-28',
        },
    ]
    return render_template('index.html', name_user=name_user, list_ha=list_ha)


if __name__ == "__main__":
    app.run(debug=True)
