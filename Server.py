from typing_extensions import Required
from flask import Flask, render_template
from flask import request
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import *
from config import Config

app = Flask(__name__)
app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
moment = Moment(app)
#manager = Manager(app)

# Form class
class myform(Form):
    name = StringField('Name', validators=[Required()])
    submit = SubmitField('Submit')
@app.route("/")
def home():
    return render_template('index.html', current_time = datetime.utcnow())
@app.route("/Fefal")
def fefal():
    return "Welcome back, your majesty"
@app.route("/user/<name>")
def opps(name):
    return render_template('user.html', name = name)
@app.route("/GetBrowser")
def GB():
    return f"Your browser is {request.headers.get('User-Agent')}"
@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
 return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
    #manager.run()