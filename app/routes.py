from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, PollCreationForm, RecipesCreationForm
from app.models import User, Poll, Recipe


# renders home
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


# renders login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # when user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # when user has different username or password
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        # redirects back to the previous link before redirected to login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


# logout, login required
@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# renders register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)  # adds to the database
        db.session.commit()  # commits all the changes in the database
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# TODO
# renders account, login required
@app.route('/account')
def account():
    return render_template('account.html', title='My Account')


# TODO
# renders polls, login required
@app.route('/polls')
def polls():
    return render_template('polls.html', title='Polls')


# TODO
# renders users, admin only
@app.route('/users')
def users():
    return render_template('users.html', title='Users Management')


# TODO
# admin page to manage polls
@app.route('/manage_polls')
def manage_polls():
    return render_template(
        'manage_polls.html',
        title='Manage Polls',
        poll=Poll,
        recipe=Recipe)


# TODO
# admin page to manage users
@app.route('/manage_users')
def manage_users():
    return render_template('manage_users.html', title='Manage Users')


# TODO
# admin page to add recipes
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = RecipesCreationForm()

    form.poll.choices = [
        (poll.id, poll.name) for poll in Poll.query.order_by('date_created')]

    if form.validate_on_submit():
        recipe = Recipe(
            name=form.name.data,
            description=form.description.data,
            contributor_id=current_user.id,
            poll_id=form.poll.data
            )

        db.session.add(recipe)  # adds to the database
        db.session.commit()  # commits all the changes in the database
        flash('Added to database')
        return redirect(url_for('add_recipe'))

    return render_template('add_recipe.html', title='Add Recipe', form=form)

# TODO
# admin page to add polls
@app.route('/add_poll', methods=['GET', 'POST'])
def add_poll():
    form = PollCreationForm()

    if form.validate_on_submit():
        poll = Poll(
            name=form.name.data,
            description=form.description.data,
            creator_id=current_user.id
        )

        db.session.add(poll)
        db.session.flush()  # lets you access the generated poll.id

        for r in form.recipes:
            recipe = Recipe(
                name=r.data['name'],
                description=r.data['description'],
                contributor_id=current_user.id,
                poll_id=poll.id
            )

            db.session.add(recipe)

        db.session.commit()  # commits all the changes in the database
        flash('Added to database')
        return redirect(url_for('add_poll'))

    return render_template('add_poll.html', title='Add Poll', form=form)
