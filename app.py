import os
from flask import Flask, render_template, request
script_dir = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.abspath(script_dir)
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    # data = "Hello from Python!";
    return render_template('index.html');
@app.route('/handle', methods=['POST'])
def handle_form_submission():
    text = request.form['my_textbox']
    print(f"Value from textbox: {text}")
    return "Form data processed"
if __name__ == '__main__':
    app.run(debug=True)
