from flask import Blueprint, request, render_template, redirect, url_for, abort, session
from flask_oauthlib.client import OAuth, OAuthException

from helpers import *
import model
import user_config as config

user = Blueprint('user', __name__)

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

@user.route('/login')
def login():
    return facebook.authorize(callback=url_for('user.login_authorized',
            next=request.args.get('next') or request.referrer or None, _external=True))

@user.route('/login/authorized')
def login_authorized():
    next_url = request.args.get('next') or url_for('web.index')
    resp = facebook.authorized_response()
    if resp is None:
        return redirect(next_url)

    if isinstance(resp, OAuthException):
            return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = get_user()

    me_check = model.get_user(me['id'])
    if not me_check:
        me_db = model.User('facebook', me['id'])
        db.session.add(me_db)
        db.session.commit()

    return redirect(next_url)

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
                            added_words=results)

def user_area():
    ''' Returns the "user area" - a login button if you're not logged in
        or a profile pic and your name if you are'''
    if 'oauth_token' in session:
        me = get_user()
        pic = get_user_pic()
        # user logged in but information not getting retrieved from fb.
        if 'name' not in me: 
            return render_template('loggedout.html')
        return render_template('loggedin.html', user_pic_url=pic['url'], user_name=me['name'])
    else:
        return render_template('loggedout.html')

def get_user(service='facebook', user_id=None):
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

def get_user_pic(service='facebook', user_id=None):
    pic = facebook.get('/me/picture?redirect=false')
    return pic.data['data']
