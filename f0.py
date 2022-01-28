from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    """
    D:\myvirtualenv\venv2\Scripts>workon venv2
    (venv2) D:\myvirtualenv\venv2\Scripts>python E:\手机又没电了的云文档\001-本科生\004-辅修\005-Python_MySQL大作业\program0-2022-01-10\f0.py
    """
    return '菜菜'

if __name__ == '__main__':
    app.run()