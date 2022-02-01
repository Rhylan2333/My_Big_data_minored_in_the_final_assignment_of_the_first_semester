# 在这个脚本中加载环境变量，并导入程序实例以供部署时使用：
# 但问题是它一加到我文件根目录后，app.py 在 flask run 下就失灵了。
import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
print(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 这两个环境变量的具体定义，我们将在远程服务器环境创建新的 .env 文件写入。

import app
print("Checked.")