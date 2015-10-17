# -*- coding: utf-8 -*- 
from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for, abort, session, flash
from io import StringIO

from forms import *

import model
import collections
from flask_oauthlib.client import OAuth, OAuthException

oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=1490053241290663,
    consumer_secret='460470cd0827caa33ba93d47d4f7874d',
    request_token_params={'scope': 'email'}
)

app = Flask(__name__)
app.config.from_object('config')
app.config['SERVER_NAME'] = 'localhost:5000'


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('login_authorized',
            next=request.args.get('next') or request.referrer or None, _external=True))

@app.route('/login/authorized')
def login_authorized():
    next_url = request.args.get('next') or url_for('index')
    resp = facebook.authorized_response()
    if resp is None:
        flash(u'Login failed.')
        return redirect(next_url)

    if isinstance(resp, OAuthException):
            return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    model.add_user(me.data)

    flash('Logged in as %s' % (me.data['name']))
    return redirect(next_url)

@app.route('/logout')
def logout():
    next_url = request.args.get('next') or url_for('index')
    session.clear()
    resp = redirect(next_url)
    resp.set_cookie('session', '', expires=0)
    return resp

@app.route('/profile/delete')
def delete_profile():
    next_url = request.args.get('next') or url_for('index')
    me = get_user()
    if me is not None:
        uid = me['id']
        success = facebook.delete('/{}/permissions'.format(uid), format=None)
        if success:
            return logout()
    return redirect(next_url)

def user_area():
    ''' Returns the "user area" - a login button if you're not logged in
        or a profile pic and your name if you are'''
    if 'oauth_token' in session:
        me = get_user()
        pic = facebook.get('/me/picture?redirect=false')
        return render_template('loggedin.html', user_pic_url=pic.data['data']['url'], user_name=me['name'])
    else:
        return render_template('loggedout.html')

app.jinja_env.globals.update(user_area=user_area)

def get_user():
    try:
        me = facebook.get('/me')
    except OAuthException:
        return None
    if me is None:
        return None
    else:
        return me.data

def request_wants_json():
    """returns true if the current request has a JSON application type, false otherwise.
    This helper function from http://flask.pocoo.org/snippets/45/"""
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

@app.route('/index.html') # ET-19
@app.route('/')
def index():
    search_field = SearchForm()
    return render_template('index.html', form=search_field, landing_title="Etymograph", body_class="index")

@app.route('/search')
def search(): # ET-5, ET-19
    """
    Search for all words that match a particular substring
    usage: /search?q=<string> or frontend search bar
    """
    search_str = request.args['q']
    results = model.search(search_str)

    if not request_wants_json():
        search_field = SearchForm()
        return render_search_template('results.html',
			form=search_field,
			search_str=search_str.capitalize(),
			results=results, body_class="search")
    else:
        response = json.jsonify(results)
        return response

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), **kwargs)


@app.route('/<int:word_id>/roots')
def roots(word_id): # ET-6
    if 'depth' in request.args:
        try:
            depth = int(request.args['depth'])
            if depth < 0:
                raise ValueError
        except ValueError:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    try:
        response = json.jsonify(model.roots(word_id, depth=depth))
        response.status_code = 200
    except model.WordNotFoundException:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response


@app.route('/<int:word_id>/descs')
def descs(word_id): # ET-7
    if 'depth' in request.args:
        try:
            depth = int(request.args['depth'])
            if depth < 0:
                raise ValueError
        except ValueError:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    try:
        response = json.jsonify(model.descs(word_id, depth=depth))
        response.status_code = 200
    except model.WordNotFoundException:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response

@app.route('/<int:word_id>/info')
def info(word_id): # ET-20
    try:
        info = model.info(word_id)
    except model.WordNotFoundException as e:
        if request_wants_json():
            errNum  = 1234 # placeholder error num. TODO: change
            errDesc = str(e)
            response = json.jsonify({'error':errNum, 'description':errDesc})
            response.status_code = 404 #file not found
            return response
        else:
            # display file not found page
            abort(404)

    if request_wants_json():
        # Convert word data to JSON and wrap in a Flask response
        response = json.jsonify(info)
        response.status_code = 200 # OK
    else:
        # Non-JSON request, return info page
        response = render_search_template('info.html', word_properties=info, body_class="info")
    return response



@app.route('/add/word', methods=['GET', 'POST'])
def add_word():
    me = get_user()
    if me is not None:
        form = AddWordForm(request.form)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            word_data = form.data
            # add the word to the database
            word = Word(word_data)
            word_id = model.add_word(me, word)
            return redirect('/{}'.format(word_id))

        return render_search_template('addword.html', form=form)
    else:
        abort(403)


@app.route('/add/root', methods=['POST'])
def add_root():
    me = get_user()
    if me is not None:
        form = AddRootForm(request.form)
        word_id = form.word_id.data
        root_id = form.root_id.data
        source = form.source.data

        word = Word(word_id, model.graph)
        root = Word(root_id, model.graph)

        model.add_relationship(me, word, root, source=source)
        next_url = request.args.get('next') or '/{}'.format(word_id)
        return redirect(next_url)
    else:
        abort(403)


@app.route('/<int:word_id>')
def show_graph(word_id):
    try:
        word_roots = model.roots(word_id)
        word_descs = model.descs(word_id)
        search_field = SearchForm()
        return render_search_template('graph.html', roots=word_roots, descs=word_descs, form=AddRootForm(), body_class="graph")
    except model.WordNotFoundException:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
