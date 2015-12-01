from flask import Blueprint, request, redirect, url_for, abort, session
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user

from forms import *
import helpers
import model

user = Blueprint('user', __name__)

login_manager = LoginManager()
@user.record_once
def on_load(state):
    login_manager.setup_app(state.app)

@login_manager.user_loader
def user_loader(user_id):
    return model.User.query.get(int(user_id))

@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        user_data = form.data
        # make sure username isn't taken
        user_check = model.User.query.filter_by(username=user_data['username']).first()
        if user_check is None:
            # add the word to the database
            user = model.User(user_data['username'],
                user_data['password'],
                user_data['name'])
            model.db.session.add(user)
            model.db.session.commit()
            return redirect(url_for('user.login'))
        abort(400)

    return helpers.render_search_template('register.html', form=form, title='Register')

@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        user_data = form.data
        user = model.User.query.filter_by(username=user_data['username']).first()
        if user is not None and user.check_password(user_data['password']):
            login_user(user)
            return redirect(url_for('web.index'))
        else:
            print(user)
            abort(400)

    return helpers.render_search_template('login.html', form=form, title='Log in')

@user.route('/logout')
def logout():
    next_url = request.args.get('next') or url_for('web.index')
    logout_user()
    resp = redirect(next_url)
    resp.set_cookie('session', '', expires=0)
    return resp

@user.route('/profile/<int:user_id>')
def profile(user_id):
    user = get_user(user_id=user_id)
    is_me = (user == current_user)
    if user == None:
        return abort(400)
    results = [word.info() for word in user.created_words]
    return helpers.render_search_template('profile.html', 
                            user_name=user.name, 
                            body_class='index',
                            is_me=is_me, 
                            added_words=results,
                            title=user.name)

def user_area():
    ''' Returns the "user area" - a login button if you're not logged in
        or your name if you are'''
    # user logged in but information not getting retrieved from fb.
    if current_user.is_authenticated: 
        return helpers.render_template('loggedin.html', user_name=current_user.name)
    else:
        return helpers.render_template('loggedout.html')

def get_user(user_id=None):
    if user_id is None:
        return current_user
    else:
        return model.User.query.get(user_id)
