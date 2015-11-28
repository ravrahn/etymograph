from flask import Blueprint, request, render_template, redirect, url_for, abort, session
from flask_oauthlib.client import OAuth, OAuthException
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user

from helpers import *
import model
import user_config as config

user = Blueprint('user', __name__)

login_manager = LoginManager()
@user.record_once
def on_load(state):
    login_manager.setup_app(state.app)

@login_manager.user_loader
def user_loader(user_id):
    return model.User.query.get(int(user_id))

oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.FB_KEY,
    consumer_secret=config.FB_SECRET,
    request_token_params={'scope': 'email'}
)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

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

    return render_search_template('register.html', form=form, title='Register')

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        user_data = form.data
        user = model.User.query.filter_by(username=user_data['username']).first()
        if user is not None and user.check_password(user_data['password']):
            login_user(user)
        else:
            print(user)
            abort(400)

    return render_search_template('login.html', form=form, title='Log in')

@user.route('/logout')
def logout():
    next_url = request.args.get('next') or url_for('web.index')
    session.clear()
    resp = redirect(next_url)
    resp.set_cookie('session', '', expires=0)
    return resp

@user.route('/profile/delete')
def delete_profile():
    next_url = request.args.get('next') or url_for('web.index')
    me = get_user()
    if me is not None:
        uid = me['id']
        success = facebook.delete('/{}/permissions'.format(uid), format=None)
        if success:
            return logout()
    return redirect(next_url)

@user.route('/profile/<user_id>')
def profile(user_id):
    is_me = (user_id == 'me')
    if is_me:
        user = get_user()
    else:
        user = get_user(user_id=user_id)
        is_me = (user == get_user())
    if user == None:
        return abort(400)
    user_db = model.User.query.filter_by(token=user['id']).first()
    results = [word.info() for word in user_db.created_words]
    return render_search_template('profile.html', 
                            user_name=user['name'], 
                            body_class="index",
                            is_me=is_me, 
                            added_words=results,
                            title=user['name'])

def user_area():
    ''' Returns the "user area" - a login button if you're not logged in
        or your name if you are'''
    # user logged in but information not getting retrieved from fb.
    if current_user.is_authenticated: 
        return render_template('loggedin.html', user_name=current_user.name)
    else:
        return render_template('loggedout.html')

def get_user(user_id=None):
    try:
        if user_id is not None:
            user = facebook.get('/{}'.format(user_id))
        else:
            user = facebook.get('/me')
    except OAuthException:
        return None
    if user is None:
        return None
    else:
        return user.data
