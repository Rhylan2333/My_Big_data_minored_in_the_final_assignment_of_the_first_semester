# from flask import url_for
from flask import Flask, render_template, request
import formula
app = Flask(__name__)


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
        {'x1': '50', 'x2': '300', 'y': '25.624243', 'date': '2022-01-29', },
        {'x1': '10', 'x2': '60', 'y': '15.435247', 'date': '2022-01-25', },
        {'x1': '20', 'x2': '120', 'y': '17.6739028', 'date': '2022-01-26', },
        {'x1': '30', 'x2': '180', 'y': '20.1182874', 'date': '2022-01-27', },
        {'x1': '40', 'x2': '250', 'y': '22.768400800000002', 'date': '2022-01-28', },
    ]
    return render_template('index.html', name_user=name_user, list_ha=list_ha)

if __name__ == "__main__":
    app.run(debug=True)

