from flask import Flask, render_template
app = Flask(__name__)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('index.html', name=name)
