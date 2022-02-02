import os
import sys
from datetime import date
from email.policy import default
from enum import unique

import click
from flask import (Flask, escape, flash, redirect, render_template, request,
                   url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import \
    SQLAlchemy  # 导入扩展类。Flask-SQLAlchemy 版本 2.4.0 Apr 25, 2019 可行
from werkzeug.security import check_password_hash, generate_password_hash

import formula

# 为了部署到线上，我添加了 wsgi.py 文件，这使得我得在 cmd 中先输入 set FLASK_APP=app.py，再输入 flask run 才能运行

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)

# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址：
# SQLALCHEMY_DATABASE_URI = prefix + os.path.join(
#     app.root_path, os.getenv('myha\my_ha_data.db', 'my_ha_data.db'))
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
    os.path.dirname(app.root_path), 'myha/', os.getenv(
        'DATABASE_FILE', 'my_ha_data.db'))  # 这个在线下一用就找不到数据库的位置，添加了 'myha/' 后可以在线下了。但是！线上一定不能要它！！！

# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
#     os.path.dirname(app.root_path), os.getenv(
#         'DATABASE_FILE', 'my_ha_data.db'))  # 这个在线下一用就找不到数据库的位置，添加了 'myha/' 后可以在线下了。但是！线上一定不能要它！！！
"""上面三行就是线上的代码！！！"""

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

# 接下来创建数据库模型。
"""
    模型类要声明继承 db.Model。
    每一个类属性（字段）要实例化 db.Column，传入的参数为字段的类型。
    在 db.Column() 中添加额外的选项（参数）可以对字段进行设置。比如，primary_key 设置当前字段是否为主键。除此之外，常用的选项还有 nullable（布尔值，是否允许为空值）、index（布尔值，是否设置索引）、unique（布尔值，是否允许重复值）、default（设置默认值）等。
"""


# 管理员 表
class Admin_info(db.Model, UserMixin):  # 表名将会是 user_info （自动生成，小写处理）
    id_admin = db.Column(db.Integer, primary_key=True)  # 主键，管理员id
    name_admin = db.Column(db.String(20), unique=True)  # 管理员称呼
    list_area_info = db.relationship(
        'Area_info',
        backref='area')  # 这里新建了一个名叫 area 的属性用来表示当前模型中包含的 Area_info 列表。
    """
    第一部分 —— 'Area_info' 表示关系另一端的模型的名称。
    第二部分 —— 是一个名叫 backref 的参数，叫做反向关系，我们将其设置成 'area_info' ，
        它会向 Area_info 模型中添加一个名叫 area_info 的属性，
        这个属性可以替代 id_admin（FK） 访问 Area_info 模型，但是它获取的是 Area_info 模型的对象，而非 Area_info 模型中 id_admin（FK）对应的值。
    """
    adminname = db.Column(db.String(20))  #管理员的用户名
    password_hash = db.Column(db.String(128))  # 管理员的密码

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

    def get_id(self):
        """"表示感谢https://www.cnpython.com/qa/162793"""
        return (self.id_admin)


# 地区 表
class Area_info(db.Model):  # 表名将会是 area_info （自动生成，小写处理）
    id_area = db.Column(db.Integer, primary_key=True)  # 主键，地区id
    name_area = db.Column(db.String(20), unique=True)  # 地区名
    list_ha_info = db.relationship('Ha_info', backref='ha')
    list_user_info = db.relationship('User_info', backref='user')
    id_admin = db.Column(db.Integer,
                         db.ForeignKey('admin_info.id_admin'))  # 外键，管理员id


# 农户 表
class User_info(db.Model, UserMixin):  # 表名将会是 user_info （自动生成，小写处理）
    """
    在存储用户信息的 User 模型类添加 username 字段和 password_hash 字段，分别用来存储登录所需的用户名和密码散列值，同时添加两个方法来实现设置密码和验证密码的功能：
    
    Flask-Login 提供了一个 current_user 变量，注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录。另一个步骤是让存储用户的 User 模型类继承 Flask-Login 提供的 UserMixin 类：
    继承 UserMixin 这个类会让 User_info 类拥有几个用于判断认证状态的属性和方法，
        其中最常用的是 is_authenticated 属性：如果当前用户已经登录，那么 current_user.is_authenticated 会返回 True， 否则返回 False。
    有了 current_user 变量和这几个验证方法和属性，我们可以很轻松的判断当前用户的认证状态。
    """
    id_user = db.Column(db.Integer, primary_key=True)  # 主键，农户id
    name_user = db.Column(db.String(20), unique=True)  # 农户称呼
    list_ha_info = db.relationship('Ha_info', backref='ha_info')  # 这个功能未能实现
    username = db.Column(db.String(20), unique=True)  # 农户的用户名
    password_hash = db.Column(db.String(128))  # 农户密码
    id_area = db.Column(db.Integer,
                        db.ForeignKey('area_info.id_area'))  # 外键，农户所属地区id

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

    def get_id(self):
        """"表示感谢https://www.cnpython.com/qa/162793"""
        return (self.id_user)


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
    # 全局变量 list_…… 移动到这个函数内
    # name_user = '蔡雨豪'
    # password_hash_user = generate_password_hash('123')
    # name_admin = 'Yuhao Cai'
    # password_hash_admin = generate_password_hash('123456')

    list_admin = [{
        'id_admin': 0,
        'name_admin': '管理员0',
        'adminname': 'guanliyua',
        'password_hash': generate_password_hash('123456')
    }]  # 创建 admin 实例

    list_area = [{
        'id_area': 0,
        'name_area': "伊犁",
        'id_admin': 0  # 这是外键
    }]  # 创建 area 实例

    list_user = [{
        'id_user': 0,
        'name_user': '农户0',
        'username': 'nonghu',
        'password_hash': generate_password_hash('123'),
        'id_area': 0  # 这是外键
    }]  # 创建 user 实例

    list_ha = [{
        'id_ha': 5,
        'x1': 50,
        'x2': 300,
        'y': '25.624243',
        'date': date(2022, 1, 29),
        'id_user': 5,
        'id_area': 5
    }, {
        'id_ha': 1,
        'x1': 10,
        'x2': 60,
        'y': 15.435247,
        'date': date(2022, 1, 25),
        'id_user': 1,
        'id_area': 1
    }, {
        'id_ha': 2,
        'x1': 20,
        'x2': 120,
        'y': 17.6739028,
        'date': date(2022, 1, 26),
        'id_user': 2,
        'id_area': 2
    }, {
        'id_ha': 3,
        'x1': 30,
        'x2': 180,
        'y': 20.1182874,
        'date': date(2022, 1, 27),
        'id_user': 3,
        'id_area': 3
    }, {
        'id_ha': 4,
        'x1': 40,
        'x2': 250,
        'y': 22.768400800000002,
        'date': date(2022, 1, 28),
        'id_user': 4,
        'id_area': 4
    }]

    for row_admin in list_admin:
        """在此实现下两行 admin 实例所对应的 Admin_info 模型中定义的 list_area_info 接着由 relationship 生成的 InstrumentedList"""
        print(row_admin)
        admin = Admin_info(
            id_admin=row_admin['id_admin'],
            name_admin=row_admin['name_admin'],
            adminname=row_admin['adminname'],
            password_hash=row_admin['password_hash']
        )  # 把这个 def 中的 name_admin = 'Yuhao Cai' 左传给 Admin_info 模型中的 name_admin
        print(admin)  # 检查此实例是否创建成功
        db.session.add(admin)

    for row_area in list_area:
        print(row_area)
        area = Area_info(
            id_area=row_area['id_area'],
            name_area=row_area['name_area'],
            id_admin=row_area['id_admin']  # 这是外键
        )  # 创建实例
        print(area)  # 检查此实例是否创建成功

        admin.list_area_info.append(
            area)  # 向 admin 实例中的 relationship 生成的 list_area_info 传入 area 实例
        print(
            admin.list_area_info[-1].name_area)  # 获取 InstrumentedList 的倒数第一个元素

        db.session.add(area)

    for row_user in list_user:
        print(row_user)
        user = User_info(
            id_user=row_user['id_user'],
            name_user=row_user['name_user'],
            username=row_user['username'],
            password_hash=row_user['password_hash'],
            id_area=row_user['id_area']
        )  # 把这个 def 中的 name_user = '蔡雨豪' 左传给 User_info 模型中的 name_user
        print(user)

        area.list_user_info.append(
            user)  # 向 area 实例中的 relationship 生成的 list_user_info 传入 user 实例
        print(
            area.list_user_info[-1].name_user)  # 获取 InstrumentedList 的倒数第一个元素

        db.session.add(user)

    for row_ha in list_ha:
        print(row_ha)
        ha = Ha_info(
            id_ha=row_ha['id_ha'],
            x1=row_ha['x1'],
            x2=row_ha['x2'],
            y=row_ha['y'],
            date=row_ha['date'],
            id_user=row_ha['id_user'],
            id_area=row_ha['id_area']
        )  # 创建一个 row_ha 记录，等号左边的“x1、x2、y”与ha_info表中的“x1、x2、y”要匹配/相等
        print(ha)

        area.list_ha_info.append(
            ha
        )  # 向 area 实例中的 relationship 生成的 list_ha_info 传入 ha 实例。源自 print(area.list_ha_info)
        user.list_ha_info.append(
            ha
        )  # 向 user 实例中的 relationship 生成的 list_ha_info 传入 ha 实例。源自 print(user.list_ha_info)
        print(area.list_ha_info[-1].id_user)  # 获取 InstrumentedList 的倒数第一个元素
        print(user.list_ha_info[-1].id_area)  # 获取 InstrumentedList 的倒数第一个元素

        db.session.add(ha)

    db.session.commit()
    db.session.close()
    click.echo('虚拟数据已写入数据库 my_ha_data。')


# 为了方便数据初始化
y0 = ''  # 专门为显示 产量损失率(%) 而设计的。发现要在 if 的上一层才能成功渲染。
y00 = ''  # 为了实现非登录用户的计算功能专门做的
id_user = ''  # 为实现“用户登录后，自动获取其 id_user、name_user、username、id_area，再把这些用于写入 ha_info 表第 6、7 列的数据”这一功能
id_area = ''  # 为实现“用户登录后，自动获取其 id_user、name_user、username、id_area，再把这些用于写入 ha_info 表第 6、7 列的数据”这一功能
NAME_USER = ''  # 为了“用户登录后，自动获取其 name_user”，把 name_user 传给 base.html 的“NAME_USER”，实现“定制化您好”功能
list_area_name_area = []  # 为了实现对 ha_info 进行模糊查询，转向新的视图函数
list_area_admin_name_area = []  # 为了实现对 area_info、user_info 进行模糊查询，转向新的视图函数


@app.route('/', methods=['GET', 'POST'])
def index():
    global y0, y00, NAME_USER
    if request.method == 'POST':  # 判断是否是 POST 请求
        if not current_user.is_authenticated:  # 如果当前用户未认证，则 ta 只能使用“计算”功能
            """
            is_authenticated 的说明 见 Class User_info...
            创建新条目的操作稍微有些不同，
            因为对应的 '/' 视图同时处理显示页面的 GET 请求和创建新条目的 POST 请求，
            我们仅需要禁止未登录用户创建新条目，
            因此不能使用 login_required，而是在函数内部的 POST 请求处理代码前进行过滤：
            """
            x1 = request.form.get('x1')  # 传入表单对应输入字段的 name 值
            x2 = request.form.get('x2')
            # 验证数据
            if not x1 or not x2:
                flash('Invalid input.')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页
            else:
                try:
                    """防止输入非数字报错"""
                    y00 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(
                        eval(x1) / 50,
                        eval(x2) / 300)
                    return redirect(url_for('index'))  # 重定向回主页
                except:
                    flash('请重新输入，不要输入非数字内容！')  # 显示错误提示
                    return redirect(url_for('index'))  # 重定向回主页

        # 获取表单数据
        x1 = request.form.get('x1')  # 传入表单对应输入字段的 name 值
        x2 = request.form.get('x2')
        # 验证数据
        if not x1 or not x2:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        else:
            try:
                y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(
                    eval(x1) / 50,
                    eval(x2) / 300)
            except:
                flash('请重新输入，不要输入非数字内容！')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        global id_user, id_area
        row_ha = Ha_info(
            # id_ha 自增，不必写入
            x1=x1,
            x2=x2,
            y=y0,
            date=date.today(),
            id_user=id_user,  # 需要从 登录用户 获取。这里 global 来的 id_user 已经被登录界面赋值了！
            id_area=
            id_area,  # 需要从 登录用户 获取，参考 test_fk.py。这里 global 来的 id_area 已经被登录界面赋值了！
        )  # 创建记录。
        # row_ha = Ha_info(x1=x1, x2=x2, date=date.today())  # 创建记录
        db.session.add(row_ha)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('写入成功！')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页。与下一行代码只能二选一吗？那线上计算的功能就没了。
        # return render_template('index.html', RESULT=str(y0))# 本意是重定向回主页“return redirect(url_for('index'))”
    # user_info = User_info.query.first()  # 读取农户记录。被删掉是因为有了模板上下文处理函数 inject_user()
    list_ha = Ha_info.query.order_by(db.desc(Ha_info.id_ha)).all(
    )  # 读取所有棉铃虫信息记录，并倒序排列（db.desc(Ha_info.id_ha)）。方便传给前端。
    list_ha_limit = Ha_info.query.order_by(db.desc(
        Ha_info.id_ha)).limit(10).all()  # 读取所有棉铃虫信息记录，但在主页只显示最新的 10 条。
    """<模型类>.query.<过滤方法（可选）>.<查询方法>"""
    return render_template(
        'index.html',
        Area_info=Area_info,
        User_info=User_info,
        list_ha=list_ha,
        list_ha_limit=list_ha_limit,
        RESULT=str(y0),
        RESULT_visitor=str(y00),
        NAME_USER=NAME_USER
    )  # 这里不能用 NAME_USER=current_user.name_user 了，因为“登出”后会报错。


# 对 ha_info 的全面的友好的展示。对 ha_info 进行模糊查询，转向新的视图函数
@app.route('/ha_detail', methods=['GET', 'POST'])
@login_required  # 保护
def ha_detail():
    global list_area_name_area
    if request.method == 'POST':  # 判断是否是 POST 请求
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向回主页
        # 认证完毕后获取表单数据
        fuzzy_inquiry_name_area = request.form.get(
            'fuzzy_inquiry_name_area')  # 传入表单对应输入字段的 fuzzy_inquiry_name_area 值
        # 验证数据
        try:
            list_area = Area_info.query.order_by(db.desc(
                Area_info.id_area)).filter(
                    Area_info.name_area.like(
                        "%{}%".format(fuzzy_inquiry_name_area))).all(
                        )  # 返回一个 包含“满足检索要求”的所有记录的 list
            """用到了python中的正则表达式"""
            list_area_name_area = []  # 使用前需要“清空”
            for row_area in list_area:
                list_area_name_area.append(row_area.name_area)
            """如果“伊”匹配到了“伊犁”和“伊宁”，这都会被传入"""
        except:
            flash('不合规，请重新输入！')  # 显示错误提示
            return redirect(url_for('ha_detail'))  # 重定向回主页
        # 从数据库获取……（获取保存表单数据到数据库）
        flash('查询结果如下：')
        return redirect(
            url_for('ha_detail'))  # 重定向回主页。与下一行代码只能二选一吗？那线上计算的功能就没了。
    list_ha = Ha_info.query.order_by(db.desc(Ha_info.id_ha)).all(
    )  # 读取所有棉铃虫信息记录，并倒序排列（db.desc(Ha_info.id_ha)）。之后传给前端。
    """<模型类>.query.<过滤方法（可选）>.<查询方法>"""
    return render_template(
        'ha_detail.html',
        Area_info=Area_info,
        User_info=User_info,
        list_ha=list_ha,
        list_area_name_area=list_area_name_area,
        NAME_USER=current_user.name_user
    )  # 只有登录后才能进入详细查询页，所以此时 NAME_USER=current_user.name_user 可用


# 对 area_info 的全面的友好的展示。首页点击“管理员……”即可
@app.route('/area_detail', methods=['GET', 'POST'])
@login_required  # 保护
def area_detail():
    global list_area_admin_name_area
    if request.method == 'POST':  # 判断是否是 POST 请求
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向回主页
        # 认证完毕后获取表单数据
        fuzzy_inquiry_name_area_admin = request.form.get(
            'fuzzy_inquiry_name_area_admin'
        )  # 传入表单对应输入字段的 fuzzy_inquiry_name_area_admin 值
        # 验证数据
        try:
            list_area_admin = Area_info.query.order_by(
                db.desc(Area_info.id_area)).filter(
                    Area_info.name_area.like(
                        "%{}%".format(fuzzy_inquiry_name_area_admin))).all(
                        )  # 返回一个 包含“满足检索要求”的所有记录的 list
            """用到了python中的正则表达式"""
            list_area_admin_name_area = []  # 使用前需要“清空”
            for row_area_admin in list_area_admin:
                list_area_admin_name_area.append(row_area_admin.name_area)
            """如果“伊”匹配到了“伊犁”和“伊宁”，这都会被传入"""
        except:
            flash('不合规，请重新输入！')  # 显示错误提示
            return redirect(url_for('ha_detail'))  # 重定向回主页
        # 从数据库获取……（获取保存表单数据到数据库）
        flash('查询结果如下：')
        return redirect(url_for('area_detail'))  # 重定向回 area_detail
    list_area = Area_info.query.order_by(db.desc(
        Area_info.id_area)).all()  # 读取所有地区信息记录，并倒序排列。之后传给前端，表的最左边会用到。
    return render_template('area_detail.html',
                           Area_info=Area_info,
                           User_info=User_info,
                           list_area=list_area,
                           list_area_admin_name_area=list_area_admin_name_area,
                           NAME_USER=current_user.name_user)


# 编辑 Ha_info 条目
@app.route('/ha_info/edit/<int:id_ha>', methods=['GET', 'POST'])
@login_required  #视图保护
def edit(id_ha):
    row_ha = Ha_info.query.get_or_404(id_ha)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        x1 = request.form['x1']
        x2 = request.form['x2']

        if not x1 or not x2:
            flash('Invalid input.')
            return redirect(url_for('edit', id_ha=id_ha))  # 重定向回对应的编辑页面
        else:
            y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(
                eval(x1) / 50,
                eval(x2) / 300)
        # 保存更新的表单数据到数据库
        row_ha.x1 = x1  # 更新 x1
        row_ha.x2 = x2  # 更新 x2
        row_ha.y = y0  # 更新 y
        db.session.commit()  # 提交数据库会话
        flash('记录已更新。')
        return redirect(url_for('index'))  # 重定向回主页
        """既然我们要编辑某个条目，那么必然要在输入框里提前把对应的数据放进去，以便于进行更新。在模板里，通过表单 <input> 元素的 value 属性即可将它们提前写到输入框里。"""
    return render_template('edit.html',
                           row_ha=row_ha,
                           NAME_USER=current_user.name_user)  # 传入被编辑的棉铃虫信息记录


# 删除 Ha_info 条目
@app.route('/ha_info/delete/<int:id_ha>', methods=[
    'POST'
])  # 限定只接受 POST 请求。为了安全的考虑，我们一般会使用 POST 请求来提交删除请求，也就是使用表单来实现（而不是创建删除链接）：
@login_required  # 登录保护。添加了这个装饰器后，如果未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示。
def delete(id_ha):
    row_ha = Ha_info.query.get_or_404(id_ha)  # 获取电影记录
    db.session.delete(row_ha)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('记录已删除。')
    return redirect(url_for('index'))  # 重定向回主页


# 404 错误处理函数
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    # user_info = User_info.query.first()  # 被删掉是因为有了模板上下文处理函数 inject_user()
    return render_template('404.html'), 404  # 返回模板和状态码


# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    global NAME_USER
    """现在我们可以删除 404 错误处理函数 errorhandler(404) 和主页视图函数中的 user_info 变量定义，并删除在 render_template() 函数里传入的关键字参数："""
    return dict(NAME_USER=NAME_USER)  # 需要返回字典，等同于 return {'user': user}


# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。
# session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
# app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 在部署章节中，上一行代码被改为：
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')


# 生成农户账户
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password',
              prompt=True,
              hide_input=True,
              confirmation_prompt=True,
              help='The password used to login.'
              )  # 使用 click.option() 装饰器设置的两个选项分别用来接受输入用户名和密码。
def user(username, password):
    """创建农户 user"""
    db.create_all()

    user = User_info.query.first()
    if user is not None:
        click.echo('Updating `农户` user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating `农户` user...')
        user = User_info(username=username, name_user='0号 user')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('User Created!')


# 生成管理员账户
@app.cli.command()
@click.option('--adminname', prompt=True, help='The adminrname used to login.')
@click.option('--password',
              prompt=True,
              hide_input=True,
              confirmation_prompt=True,
              help='The password used to login.'
              )  # 使用 click.option() 装饰器设置的两个选项分别用来接受输入用户名和密码。
def admin(adminname, password):
    """创建管理员 admin"""
    db.create_all()

    admin = Admin_info.query.first()
    if admin is not None:
        click.echo('Updating `管理员` admin...')
        admin.adminname = adminname
        admin.set_password(password)  # 设置密码
    else:
        click.echo('Creating `管理员` admin...')
        admin = Admin_info(adminname=adminname, name_admin='0号 admin')
        admin.set_password(password)  # 设置密码
        db.session.add(admin)

    db.session.commit()  # 提交数据库会话
    click.echo('Admin Created!')


# 初始化 Flask-Login。用于登录
login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'  # 为了让这个重定向操作正确执行，我们还需要把 login_manager.login_view 的值设为我们程序的登录视图端点（函数名），把这一行代码放到 login_manager 实例定义下面即可：
"""我不会一个 app.py 中实现即可登录“农户”，又可登录“管理员”。"""


@login_manager.user_loader
def load_user(id_user):  # 创建用户加载回调函数，接受用户 ID 作为参数
    """Flask-Login 提供了一个 current_user 变量，注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录。"""
    user = User_info.query.get(int(id_user))  # 用 ID 作为 User_info 模型的主键查询对应的用户
    return user  # 返回用户对象


# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    global id_user, id_area, NAME_USER
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # name_area = request.form['name_area']  # 这里容易出错！可以不从表单获取，而从外键。注意，记得在 login.html 里更新 <form>
        if not username or not password:
            flash('无效的输入。')
            return redirect(url_for('login'))

        row_user = User_info.query.order_by(db.desc(
            User_info.id_user)).filter_by(username=username).first(
            )  # 其实因为 username 是 UNIQUE，这里用.all()也会只返回一条记录。
        # 验证用户名和密码是否一致
        if row_user:
            """当用户名未写入 User_info，row_user 会查询不到，变成 NoneType，返回 False。这里用 if 来防止报错。 """
            if username == row_user.username and row_user.validate_password(
                    password):
                id_user = User_info.query.filter_by(username=username).first(
                ).id_user  # 就在这外键连接，用 filter_by()。这样就可以在 '/' 下把 id_user 的值赋给 row_ha 中的 id_user 了。

                id_area = User_info.query.filter_by(username=username).first(
                ).id_area  # 就在这外键连接，用 filter_by()。这样就可以在 '/' 下把 id_area 的值赋给 row_ha 中的 id_area 了。
                NAME_USER = User_info.query.filter_by(
                    username=username).first().name_user

                login_user(row_user)  # 登入用户。注意这里要选用特定的 column
                flash('登录成功')
                return redirect(url_for('index'))  # 重定向到主页
            else:
                flash('您的用户名与密码不匹配。')  # 如果验证失败，显示错误消息
                return redirect(url_for('login'))  # 重定向回登录页面
        else:
            flash('您的用户名未注册，现帮您跳至注册页')  # 如果验证失败，显示错误消息
            return redirect(url_for('register'))  # 重定向回注册
    else:
        return render_template('login.html')


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name_user = request.form['name_user']
        username = request.form['username']
        password_hash = request.form['password']
        name_area = request.form['name_area']  # 这里会想办法用外键连接实现的

        if not name_user or not username or not password_hash:
            flash('无效的输入。')
            return redirect(url_for('register'))  # 重定向回注册页面
        else:
            # 验证是否被注册
            if User_info.query.filter_by(
                    username=username).first() or User_info.query.filter_by(
                        name_user=name_user).first():
                flash('“称呼”或用户名已被注册，请更改用户名。')  # 如果验证失败，显示错误消息
                return redirect(url_for('register'))

            # 信息写入 Area_info
            else:
                row_area = Area_info(name_area=name_area)
            if Area_info.query.filter_by(name_area=name_area).first():
                flash('这个地区不止您一位注册')  # 如果验证失败，显示错误消息
                db.session.commit(
                )  # 先把 name_area 提交数据库的 area_info 表中，这将自动生成 id_area。管理员的 id_admin 先不管了。
            else:
                flash('在这个地区，您是第一位注册')
                db.session.add(row_area)  # 添加到数据库会话
                db.session.commit(
                )  # 先把 name_area 提交数据库的 area_info 表中，这将自动生成 id_area。管理员的 id_admin 先不管了。

            # 信息写入 User_info
            row_user = User_info(
                name_user=name_user,
                username=username,
                password_hash=generate_password_hash(password_hash),
                id_area=Area_info.query.filter_by(name_area=name_area).first().
                id_area  # 这里用外键，filter_by()。借助先前把 name_area提交数据库的 area_info 表中自动生成的 id_area。
            )
            db.session.add(row_user)  # 添加到数据库会话
            db.session.commit()  # 提交数据库会话
            flash('注册成功。已跳转至登录页，请登录')  # 如果验证失败，显示错误消息
            return redirect(url_for('login'))
    else:
        return render_template('register.html')


# 与登录相对，登出操作则需要调用 logout_user() 函数，使用下面的视图函数实现
@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    global y0, y00, id_user, id_area, NAME_USER, list_area_name_area, list_area_admin_name_area  # VSC 绝了，可以知道这一行 global 来的变量在哪被“修改过！！！”
    """初始化"""
    y0 = ''
    y00 = ''
    id_user = ''
    id_area = ''
    NAME_USER = ''
    list_area_name_area = []  # 虽然说每次查询前都要清空，但……这里会不会出现“头咬尾巴”的情况啊
    list_area_admin_name_area = []
    logout_user()  # 登出用户
    flash('再见~')
    return redirect(url_for('index'))  # 重定向回首页


# 支持设置、更改用户名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name_user = request.form['name_user']
        username = request.form['username']

        if not name_user:
            flash('无效的输入。')
            return redirect(url_for('settings'))
        if User_info.query.filter_by(
                username=username).first() and User_info.query.filter_by(
                    name_user=name_user).first():
            """这里完成判断“是否已被注册”用“and”，登录情况要用“or”。"""
            flash('“称呼”或用户名已被注册，请更改用户名。')  # 如果验证失败，显示错误消息
            return redirect(url_for('settings'))
        current_user.name_user = name_user
        current_user.username = username
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User_info.query.first()
        # user_info.name = name
        db.session.commit()
        flash('您的“称呼”与“用户名”设置成功。')
        return redirect(url_for('index'))

    return render_template('settings.html', NAME_USER=current_user.name_user)


if __name__ == "__main__":
    app.run(debug=True)
