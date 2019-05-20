from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, UserForm, PollForm, RecipeForm
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
            flash('Invalid username or password!', 'warning')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        # redirects back to the previous link before redirected to login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template(
        'login.html',
        title='Sign In',
        description='Enter your details to login',
        legend='Login Form',
        form=form)


# logout
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    else:
        flash('Already logged out!', 'info')
    return redirect(url_for('index'))


# renders register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)  # adds to the database
        db.session.commit()  # commits all the changes in the database
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template(
        'user_form.html',
        title='Register',
        description='Fill the form to create an Account',
        legend='Registration Form',
        form=form)


# renders all polls for standard users, login required
@app.route('/polls')
@login_required
def polls():
    return render_template(
        'polls.html',
        title='Polls',
        description='Information on the polls',
        polls=Poll,
        votes=Vote)


# renders all polls for non logged in
@app.route('/general_polls')
def general_polls():
    return render_template(
        'general_polls.html',
        description='General information on the polls',
        title='Polls',
        polls=Poll)


# admin page to manage users
@app.route('/manage_users')
@login_required
def manage_users():
    if current_user.is_admin:
        return render_template(
            'manage_users.html',
            title='Manage Users',
            description='Welcome Admin ' + current_user.username,
            users=User)
    else:
        abort(403)


# add new user, admin only, can create admins
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.is_admin:
        form = UserForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_admin=form.is_admin.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('The user is added', 'success')
            return redirect(url_for('add_user'))
        return render_template(
            'user_form.html',
            title='Add User',
            description='Fill in the details of the user',
            legend='Add a User',
            form=form)
    else:
        abort(403)


# renders a page for a user with given id
@app.route('/user/<int:user_id>')
@login_required
def user(user_id):
    if current_user.is_admin and current_user.id != user_id:
        user = User.query.get_or_404(user_id)
        return render_template(
            'user.html',
            title=user.username + ' - User',
            description='Information about this user',
            user=user,
            polls=Poll,
            recipes=Recipe)
    elif current_user.id == user_id:
        return render_template(
            'user.html',
            title='My Account',
            description='Welcome ' + current_user.username,
            user=current_user,
            polls=Poll,
            recipes=Recipe,
            votes=Vote)
    else:
        abort(403)


# TODO new and old passwords
# updates a user with given id, current logged in user only
@app.route('/user/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    if current_user.id == user_id:
        user = User.query.get_or_404(user_id)
        form = UserForm()
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('user', user_id=user.id))

        elif request.method == 'GET':
            form.username.data = user.username
            form.email.data = user.email

        return render_template(
            'user_form.html',
            title='Update My Account',
            description='Fill in the details to be changed',
            form=form)
    else:
        abort(403)


# deletes a user with given id
@app.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if current_user.is_admin and current_user.id != user_id:
        user = User.query.get_or_404(user_id)

        for p in Poll.query.filter_by(creator_id=user.id).all():
            delete_poll(p.id)

        for r in Recipe.query.filter_by(contributor_id=user.id).all():
            delete_recipe(r.id)

        for v in Vote.query.filter_by(user_id=user.id).all():
            delete_vote(v.id)

        db.session.delete(user)
        db.session.commit()
        flash('The user has been deleted!', 'success')
        return redirect(url_for('manage_users'))
    elif current_user.id == user_id:

        for p in Poll.query.filter_by(creator_id=user.id).all():
            delete_poll(p.id)

        for r in Recipe.query.filter_by(contributor_id=user.id).all():
            delete_recipe(r.id)

        for v in Vote.query.filter_by(contributor_id=user.id).all():
            delete_vote(v.id)

        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been deleted!', 'success')
        return redirect(url_for('index'))


# admin page to manage polls
@app.route('/manage_polls')
@login_required
def manage_polls():
    if current_user.is_admin:
        return render_template(
            'manage_polls.html',
            title='Manage Polls',
            description='Welcome Admin ' + current_user.username,
            polls=Poll,
            recipes=Recipe,
            users=User)
    else:
        abort(403)  # error 403 forbidden, no access if not admin


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

        return render_template(
            'poll_form.html',
            title='Create Poll',
            description='Fill in the details of the poll',
            legend='Create a Poll',
            form=form)
    else:
        abort(403)


# admin page to add recipes
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if current_user.is_admin:
        form = RecipeForm()

        form.poll.choices = [
            (poll.id, poll.name) for poll in Poll.query.order_by(
                'date_created')]

        if form.validate_on_submit():
            recipe = Recipe(
                name=form.name.data,
                description=form.description.data,
                contributor_id=current_user.id,
                poll_id=form.poll.data
            )

            db.session.add(recipe)  # adds to the database
            db.session.commit()  # commits all the changes in the database
            flash('The recipe has been added', 'success')
            return redirect(url_for('add_recipe'))

        return render_template(
            'recipe_form.html',
            title='Add Recipe',
            description='Fill in the details of the recipe',
            legend='Add a Recipe',
            form=form)
    else:
        abort(403)


# delete vote
@app.route('/vote/<int:vote_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_vote(vote_id):
    if current_user.is_admin:
        vote = Vote.query.filter_by(id=vote_id).first()
        recipe_id = vote.recipe_id

        db.session.delete(vote)
        db.session.commit()
        flash('The vote was deleted', 'success')
        return redirect(url_for('recipe', recipe_id=recipe_id))
    else:
        print("ABORT")
        abort(403)


# renders the page for a poll with given id
@app.route('/poll/<int:poll_id>')
@login_required
def poll(poll_id):
    if current_user.is_admin:
        poll = Poll.query.get_or_404(poll_id)  # gives 404 if not found
        return render_template(
            'poll.html',
            title=poll.name + ' - Poll',
            description='Information about this poll',
            users=User,
            poll=poll)
    else:
        abort(403)


# renders the results page for a poll with given id
@app.route('/poll/<int:poll_id>/result')
def poll_result(poll_id):
    if current_user.is_authenticated:
        poll = Poll.query.get_or_404(poll_id)  # gives 404 if not found
        return render_template(
            'poll_result.html',
            title=poll.name + ' - Results',
            description='The information about the results of this poll',
            poll=poll,
            votes=Vote)
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

            flash('You have already voted in that poll!', 'warning')
            return redirect(url_for('polls'))

        vote = Vote(
            poll_id=poll.id,
            user_id=current_user.id,
            recipe_id=recipe_id
        )

        db.session.add(vote)
        db.session.commit()
        flash('Voted succesfully!', 'success')
        return redirect(url_for('polls'))
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

        return render_template(
            'poll_form.html',
            title='Update - ' + poll.name + ' - Poll',
            description='Fill in the details to be changed',
            legend='Update - ' + poll.name + ' - Poll',
            form=form)
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
            delete_recipe(r.id)

        db.session.delete(poll)
        db.session.commit()
        flash('The poll has been deleted!', 'success')
        return redirect(url_for('manage_polls'))
    else:
        abort(403)


# renders the page for a recipe with given id
@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)
        return render_template(
            'recipe.html',
            title=recipe.name + ' - Recipe',
            description='Information about this recipe',
            users=User,
            polls=Poll,
            recipe=recipe,
            votes=Vote)
    else:
        abort(403)


# updates a recipe with given id
@app.route("/recipe/<int:recipe_id>/update", methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)
        form = RecipeForm()
        form.poll.choices = [(poll.id, poll.name)
                             for poll in Poll.query.order_by('date_created')]

        if form.validate_on_submit():
            recipe.name = form.name.data
            recipe.description = form.description.data
            recipe.poll = Poll.query.filter_by(id=form.poll.data).first()
            db.session.commit()
            flash('The recipe has been updated!', 'success')
            return redirect(url_for('recipe', recipe_id=recipe.id))

        elif request.method == 'GET':
            form.name.data = recipe.name
            form.description.data = recipe.description
            form.poll.data = recipe.poll.id

        return render_template(
            'recipe_form.html',
            title='Update - ' + recipe.name + ' - Recipe',
            description='Fill in the details to be changed',
            legend='Update - ' + recipe.name + ' - Recipe',
            form=form)
    else:
        abort(403)


# delete a recipe with given id
@app.route("/recipe/<int:recipe_id>/delete", methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    if current_user.is_admin:
        recipe = Recipe.query.get_or_404(recipe_id)

        for v in Vote.query.filter_by(recipe_id=recipe_id).all():
            delete_vote(v.id)

        db.session.delete(recipe)
        db.session.commit()
        flash('The recipe has been deleted!', 'success')
        return redirect(url_for('manage_polls'))
    else:
        abort(403)
