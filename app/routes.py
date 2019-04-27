from flask import render_template, flash, redirect, url_for
from app import app

from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'user'}
    return render_template('index.html', title='Home', user=user)


@app.route('/account', methods=['GET', 'POST'])
def account():
    """Renders the account page."""
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me ={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for(account))
    return render_template('account.html', title='Account', form=form)


@app.route('/polls')
def polls():
    """Renders the polls page."""
    return render_template('polls.html', title='Polls')


@app.route('/register')
def register():
    """Renders the register page."""
    return render_template('register.html', title='Register')