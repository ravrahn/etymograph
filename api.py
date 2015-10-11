from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for, abort, session, flash
from io import StringIO

from forms import SearchForm

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
    return facebook.authorize(callback=url_for('oauth_authorized',
            next=request.args.get('next') or request.referrer or None, _external=True))

@app.route('/login/authorized')
def oauth_authorized():
    next_url = request.args.get('next') or url_for('index')
    resp = facebook.authorized_response()
    if resp is None:
        flash(u'Login failed.')
        return redirect(next_url)

    if isinstance(resp, OAuthException):
            return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    flash('Logged in as id=%s name=%s redirect=%s' % (me.data['id'], me.data['name'], request.args.get('next')))
    return redirect(next_url)


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
    return render_template('index.html', form=search_field, landing_title="Etymograph")

@app.route('/search')
def search(): # ET-5, ET-19
    """
    Search for all words that match a particular substring
    usage: /search?q=<string> or frontend search bar
    """
    search_str = request.args['q']
    results = model.search(search_str)

    if not request_wants_json():
        return render_template('results.html',
                search_str=search_str.capitalize(),
                results=results)
    else:
        response = json.jsonify(results)
        return response


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
        response = render_template('info.html', word_properties=info)
    return response


@app.route('/<int:word_id>')
def show_graph(word_id):
    try:
        word_roots = model.roots(word_id)
        word_descs = model.descs(word_id)
        return render_template('graph.html', roots=word_roots, descs=word_descs)
    except model.WordNotFoundException:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
