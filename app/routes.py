from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, PollForm, RecipeForm
from app.models import User, Poll, Recipe, Vote


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


# logout
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    else:
        flash('Already logged out!')
    return redirect(url_for('index'))


# renders register for new account
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
# renders a user's account page, login required
@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='My Account', user=current_user)


# TODO
# renders all polls for standard users, login required
@app.route('/polls')
@login_required
def polls():
    return render_template('polls.html', title='Polls', poll=Poll, vote=Vote)


# admin page to manage polls
@app.route('/manage_polls')
@login_required
def manage_polls():
    if current_user.is_admin:
        return render_template('manage_polls.html', title='Manage Polls', polls=Poll, recipes=Recipe)
    else:
        abort(403) # error 403 forbidden, no access if not admin


# admin page to manage users
@app.route('/manage_users')
@login_required
def manage_users():
    if current_user.is_admin:
        return render_template('manage_users.html', title='Manage Users', users=User)
    else:
        abort(403)


# admin page to add polls
@app.route('/add_poll', methods=['GET', 'POST'])
@login_required
def add_poll():
    if current_user.is_admin:
        form = PollForm()

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
            flash('The poll is added', 'success')
            return redirect(url_for('add_poll'))

        return render_template('submit_poll.html', title='Create Poll', form=form, legend='Create a Poll')
    else:
        abort(403)


# admin page to add recipes
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if current_user.is_admin:
        form = RecipeForm()

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
            flash('The recipe is added', 'success')
            return redirect(url_for('add_recipe'))

        return render_template('submit_recipe.html', title='Add Recipe', form=form, legend='Add a Recipe')
    else:
        abort(403)


# renders the page for a poll with given id
@app.route('/poll/<int:poll_id>')
@login_required
def poll(poll_id):
    if current_user.is_admin:
        poll = Poll.query.get_or_404(poll_id)  # gives 404 if not found
        return render_template('poll.html', title=poll.name + ' - Poll', users=User, poll=poll)
    else:
        abort(403)


# renders the results page for a poll with given id
@app.route('/poll/<int:poll_id>/result')
@login_required
def poll_result(poll_id):
    if current_user.is_authenticated:
        poll = Poll.query.get_or_404(poll_id)  # gives 404 if not found
        return render_template('poll_result.html', title=poll.name, poll=poll)
    else:
        abort(403)


# votes for a recipe with given id
@app.route('/recipe/<int:recipe_id>/vote', methods=['GET', 'POST'])
@login_required
def vote_recipe(recipe_id):
    if current_user.is_authenticated:
        recipe = Recipe.query.get_or_404(recipe_id)  # gives 404 if not found
        poll = Poll.query.get_or_404(recipe.poll_id)

        if Vote.query.filter_by(poll_id=poll.id,
                                user_id=current_user.id
                                ).first():  # already has a vote

            flash('You have already voted in that poll')
            return render_template('polls.html', title='Polls', poll=Poll)

        vote = Vote(
            poll_id=poll.id,
            user_id=current_user.id
            )

        recipe.votes_count += 1

        db.session.add(vote)
        db.session.commit()
        flash('Voted succesfully')
        return render_template('polls.html', title='Polls', poll=Poll, vote=Vote)
    else:
        abort(403)


# TODO
# updates a poll with given id
@app.route("/poll/<int:poll_id>/update", methods=['GET', 'POST'])
@login_required
def update_poll(poll_id):
    if current_user.is_admin:
        poll = Poll.query.get_or_404(poll_id)
        form = PollForm()

        if form.validate_on_submit():
            poll.name = form.name.data
            poll.description = form.description.data

            for r in form.recipes.data:
                recipe = Recipe.query.get(r.id)
                recipe.name = r.data['name']
                recipe.description = r.data['description']
            
            db.session.commit()
            flash('The poll has been updated!', 'success')
            return redirect(url_for('poll', poll_id=poll.id))

        elif request.method == 'GET':
            form.name.data = poll.name
            form.description.data = poll.description

            # TODO existing recipes show up

        return render_template('submit_poll.html', title='Update - ' + poll.name + ' - Poll', form=form, legend='Update - ' + poll.name + ' - Poll')
    else:
        abort(403)


# delete a poll with given id including all the recipes in the poll
@app.route("/poll/<int:poll_id>/delete", methods=['POST'])
@login_required
def delete_poll(poll_id):
    if current_user.is_admin:
        poll = Poll.query.get_or_404(poll_id)
        recipes = Recipe.query.filter_by(poll_id=poll.id).all()
        for r in recipes:
            db.session.delete(r)
        db.session.delete(poll)
        db.session.commit()
        flash('The poll has been deleted!', 'success')
        return redirect(url_for('manage_polls'))
    else:
        abort(403)


# renders the page for a recipe with given id
@app.route('/recipe/<int:recipe_id>')
@login_required
def recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)
        return render_template('recipe.html', title=recipe.name + ' - Recipe', users=User, polls=Poll, recipe=recipe)
    else:
        abort(403)


# updates a recipe with given id
@app.route("/recipe/<int:recipe_id>/update", methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)
        form = RecipeForm()
        form.poll.choices = [(poll.id, poll.name) for poll in Poll.query.order_by('date_created')]
        
        if form.validate_on_submit():
            recipe.name = form.name.data
            recipe.description = form.description.data
            recipe.poll = Poll.query.filter_by(id=form.poll.data).first() # TODO might be changed when database schema is changed
            db.session.commit()
            flash('The recipe has been updated!', 'success')
            return redirect(url_for('recipe', recipe_id=recipe.id))

        elif request.method == 'GET':
            form.name.data = recipe.name
            form.description.data = recipe.description
            form.poll.data = recipe.poll.id # TODO might be changed when database schema is changed

        return render_template('submit_recipe.html', title='Update - ' + recipe.name + ' - Recipe', form=form, legend='Update - ' + recipe.name + ' - Recipe')
    else:
        abort(403)


# delete a recipe with given id
@app.route("/recipe/<int:recipe_id>/delete", methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        flash('The recipe has been deleted!', 'success')
        return redirect(url_for('manage_polls'))
    else:
        abort(403)
