import os
from flask import Flask, render_template, request, redirect

script_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(script_dir)
app = Flask(__name__, template_folder=template_dir, static_folder='static')

# Array to store answers
answers = []

# Question 1 - define a route for question 1
@app.route('/question1', methods=['POST', 'GET'])
def question1():
    if request.method == 'POST':
        answer = request.form.getlist('answer')
        answers.append(answer)
        return redirect('/question2')
    return render_template("q1.html")

# Question 2 - define a route for question 2
@app.route('/question2', methods=['POST', 'GET'])
def question2():
    if request.method == 'POST':
        answer = request.form.getlist('answer')
        answers.append(answer)
        return redirect('/question3')
    return render_template("q2.html")

# Question 3 - define a route for question 3
@app.route('/question3', methods=['POST', 'GET'])
def question3():
    if request.method == 'POST':
        answer = request.form.getlist('answer')
        answers.append(answer)
        return redirect('/result')
    return render_template("q3.html")

@app.route('/result')
def res():
    return f"<h1>Answers: {answers}</h1>";
if __name__ == '__main__':
    app.run(debug=True)
