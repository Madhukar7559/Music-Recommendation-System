import os;
from flask import Flask, render_template, request, redirect
script_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(script_dir)
app = Flask(__name__, template_folder=template_dir, static_folder='static')
answers = []

@app.route('/')
def home():
    return redirect('/question1')

@app.route('/question1', methods=['GET', 'POST'])
def question1():
    print("One Done");
    if request.method == 'POST':
        answer = request.form['answer']
        answers.append(answer)
        return redirect('/question2')
    return render_template('q1.html')

@app.route('/question2', methods=['GET', 'POST'])
def question2():
    print("Two Done");
    if request.method == 'POST':
        answer = request.form['answer']
        answers.append(answer)
        return redirect('/question3')
    return render_template('q2.html')

@app.route('/question3', methods=['GET', 'POST'])
def question3():
    print("Three Done");
    if request.method == 'POST':
        answer = request.form['answer']
        answers.append(answer)
        return redirect('/result')
    return render_template('q3.html')

@app.route('/result')
def result():
    return f"<h1>Answers: {', '.join(answers)}</h1>"

if __name__ == '__main__':
    app.run(debug=True)