from distutils.command.config import config
from multiprocessing import managers
import os
from app import create_app
from flask_script import Manager
from flask_migrate import MigrateCommand
# 获取配置
config_name = os.environ.get('FLASK_CONFIG') or 'default'
# 创建 Flask 实例
app = create_app(config_name)
# 创建命令行启动控制对象
manager = Manager(app)
# 添加数据库迁移命令
manager.add_command('db', MigrateCommand)
# 启动项目
if __name__ == '__main__':
    """通过 python E:\手机又没电了的云文档\001-本科生\004-辅修\005-Python_MySQL大作业\program0-2022-01-10\manage.py runserver -r -d 运行项目"""
    app.run()