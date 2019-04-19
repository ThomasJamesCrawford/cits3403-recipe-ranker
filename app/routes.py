from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'user'}
    return render_template('index.html', title='Home', user=user)

@app.route('/account')
def account():
    """Renders the account page."""
    return render_template('account.html')

@app.route('/polls')
def polls():
    """Renders the polls page."""
    return render_template('polls.html')

@app.route('/register')
def register():
    """Renders the register page."""
    return render_template('register.html')