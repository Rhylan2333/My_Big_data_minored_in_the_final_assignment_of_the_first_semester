import os
import sys
from datetime import date
from email.policy import default
from enum import unique

import click
from flask import (Flask, escape, flash, redirect, render_template, request,
                   url_for)
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

# 接下来创建数据库模型。
"""
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
    pwd_user = '123'
    name_admin = 'Yuhao Cai'
    pwd_admin = '123456'
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
        name_user=name_user, pwd_user=pwd_user
    )  # 把这个 def 中的 name_user = '蔡雨豪' 左传给 User_info 模型中的 name_user
    print(user)
    db.session.add(user)

    admin = Admin_info(
        name_admin=name_admin, pwd_admin=pwd_admin
    )  # 把这个 def 中的 name_admin = 'Yuhao Cai' 左传给 Admin_info 模型中的 name_admin
    print(admin)
    db.session.add(admin)

    for row_ha in list_ha:
        print(row_ha)
        ha = Ha_info(
            x1=row_ha['x1'],
            x2=row_ha['x2'],
            y=row_ha['y'],
            date=row_ha['date']
        )  # 创建一个 row_ha 记录，等号左边的“x1、x2、y”与ha_info表中的“x1、x2、y”要匹配/相等
        print(ha)
        db.session.add(ha)

    db.session.commit()
    db.session.close()
    click.echo('虚拟数据已写入数据库 my_ha_data。')


@app.route('/', methods=['GET', 'POST'])
def index():
    y0 = ''
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        x1 = request.form.get('x1')  # 传入表单对应输入字段的 name 值
        x2 = request.form.get('x2')
        # 验证数据
        if not x1 or not x2:
            """
             or type(x1) != type(50.0) or type(x1) != type(50) or type(x2) != type(300.0) or type(x2) != type(300):
            """
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        else:
            y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(
                eval(x1) / 50,
                eval(x2) / 300)
        # 保存表单数据到数据库
        row_ha = Ha_info(x1=x1, x2=x2, y=y0, date=date.today())  # 创建记录
        # row_ha = Ha_info(x1=x1, x2=x2, date=date.today())  # 创建记录
        db.session.add(row_ha)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('写入成功！')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页。与下一行代码只能二选一吗？那线上计算的功能就没了。
        # return render_template('index.html', RESULT=str(y0))# 本意是重定向回主页“return redirect(url_for('index'))”
    # user_info = User_info.query.first()  # 读取农户记录。被删掉是因为有了模板上下文处理函数 inject_user()
    list_ha = Ha_info.query.all()  # 读取所有棉铃虫信息记录
    return render_template('index.html', list_ha=list_ha, RESULT=str(y0))


@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == "POST":
        X1 = eval(request.form.get('x1')) / 50
        X2 = eval(request.form.get('x2')) / 300
        Y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(X1, X2)
        return render_template('index.html', RESULT=str(Y0))
    return render_template('index.html')  # 返回渲染好的模板作为响应


# def show_list_ha():
#     # 定义虚拟数据
#     name_user = '蔡雨豪'
#     list_ha = [
#         {
#             'x1': '50',
#             'x2': '300',
#             'y': '25.624243',
#             'date': '2022-01-29',
#         },
#         {
#             'x1': '10',
#             'x2': '60',
#             'y': '15.435247',
#             'date': '2022-01-25',
#         },
#         {
#             'x1': '20',
#             'x2': '120',
#             'y': '17.6739028',
#             'date': '2022-01-26',
#         },
#         {
#             'x1': '30',
#             'x2': '180',
#             'y': '20.1182874',
#             'date': '2022-01-27',
#         },
#         {
#             'x1': '40',
#             'x2': '250',
#             'y': '22.768400800000002',
#             'date': '2022-01-28',
#         },
#     ]
#     return render_template('index.html', name_user=name_user, list_ha=list_ha)


# 404 错误处理函数
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user_info = User_info.query.first()  # 被删掉是因为有了模板上下文处理函数 inject_user()
    return render_template('404.html'), 404  # 返回模板和状态码


# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    """现在我们可以删除 404 错误处理函数 errorhandler(404) 和主页视图函数中的 user_info 变量定义，并删除在 render_template() 函数里传入的关键字参数："""
    user_info = User_info.query.first()
    return dict(user_info=user_info)  # 需要返回字典，等同于 return {'user': user}


# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。
# session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'

if __name__ == "__main__":
    app.run(debug=True)
