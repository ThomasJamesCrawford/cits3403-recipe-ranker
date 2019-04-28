from flask import render_template, flash, redirect, url_for
from app import app, db

from flask_login import current_user, login_user, logout_user

from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user=current_user)


@app.route('/account', methods=['GET', 'POST'])
def account():
    if current_user.is_authenticated:
        # already logged in
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # no user with that email or password is wrong
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('account'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('account.html', title='Account', form=form)


@app.route('/polls')
def polls():
    """Renders the polls page."""
    return render_template('polls.html', title='Polls')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)  # add user to database
        db.session.commit()
        flash('Account registration succesful')
        return redirect(url_for('account'))

    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))