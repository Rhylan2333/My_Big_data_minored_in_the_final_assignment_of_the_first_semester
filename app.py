# from flask import url_for
from flask import Flask, render_template, request
import formula
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        X1 = eval(request.form.get('left')) / 50
        X2 = eval(request.form.get('right')) / 300
        Y0 = formula.cal_the_complex_of_1_and_2_generation_of_Ha_0(X1, X2)
        return render_template('index.html', RESULT=str(Y0))
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
