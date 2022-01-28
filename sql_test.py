from app import User, Movie, db  # 导入模型类、db变量

# 创建：
# 下面的操作演示了如何向数据库中添加记录
user = User(name='Grey Li')  # 创建一个 User 记录
m1 = Movie(title='Leon', year='1994')  # 创建一个 Movie 记录
m2 = Movie(title='Mahjong', year='1996')  # 再创建一个 Movie 记录
db.session.add(user)  # 把新创建的记录添加到数据库会话
db.session.add(m1)
db.session.add(m2)
"""在实例化模型类的时候，我们并没有传入 id 字段（主键），因为 SQLAlchemy 会自动处理这个字段。"""
db.session.commit()  # 提交数据库会话，只需要在最后调用一次即可。
"""最后一行 db.session.commit() 很重要，只有调用了这一行才会真正把记录提交进数据库，前面的 db.session.add() 调用是将改动添加进数据库会话（一个临时区域）中。"""

# 读取：
# 通过对模型类的 query 属性调用可选的过滤方法和查询方法，我们就可以获取到对应的单个或多个记录（记录以模型类实例的形式表示）。查询语句的格式如下：
# <模型类>.query.<过滤方法（可选）>.<查询方法>
# 下面的操作演示了如何从数据库中读取记录，并进行简单的查询：
movie = Movie.query.first()  # 获取 Movie 模型的第一个记录（返回模型类实例）

print(movie.title)  # 对返回的模型类实例调用属性即可获取记录的各字段数据

print(movie.year)

sql1 = Movie.query.all()  # 获取 Movie 模型的所有记录，返回包含多个模型类实例的列表

sql2 = Movie.query.count()  # 获取 Movie 模型所有记录的数量

sql3 = Movie.query.get(1)  # 获取主键值为 1 的记录

sql4 = Movie.query.filter_by(
    title='Mahjong').first()  # 获取 title 字段值为 Mahjong 的记录

sql5 = Movie.query.filter(
    Movie.title == 'Mahjong').first()  # 等同于上面的查询，但使用不同的过滤方法

# 更新
# 下面的操作更新了 Movie 模型中主键为 2 的记录：
movie = Movie.query.get(2)
movie.title = 'WALL-E'  # 直接对实例属性赋予新的值即可
movie.year = '2008'
db.session.commit()  # 注意仍然需要调用这一行来提交改动
print(Movie.query.get(2).title, Movie.query.get(2).year)  # 获取主键值为 2 的记录

# 删除
# 下面的操作删除了 Movie 模型中主键为 1 的记录：
movie = Movie.query.get(1)
db.session.delete(movie)  # 使用 db.session.delete() 方法删除记录，传入模型实例
db.session.commit()  # 提交改动