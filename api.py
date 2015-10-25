# -*- coding: utf-8 -*-
from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for, abort, session, flash
from io import StringIO

from forms import *

import model
import collections
from flask_oauthlib.client import OAuth, OAuthException
from reverse_proxy import *

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
# if you want to deploy the server, comment this line out:
app.config['SERVER_NAME'] = 'localhost:5000'
# and uncomment these two:
# app.config['SERVER_NAME'] = 'etymograph.com'
# app.wsgi_app = ReverseProxied(app.wsgi_app)
# and push it



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

@app.route('/profile/<user_id>')
def profile(user_id):
    is_me = (user_id == 'me')
    if is_me:
        user = get_user()
    else:
        user = get_user(user_id=user_id)
        is_me = (user == get_user())
    if user == None:
        return abort(400)
    results = model.user_added_word(user['id'])
    return render_search_template('profile.html', 
                            user_name=user['name'], 
                            body_class="index",
                            is_me=is_me, 
                            added_words=results)

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
        # user logged in but information not getting retrieved from fb.
        if 'data' not in pic.data or 'name' not in me: 
            return render_template('loggedout.html')
        return render_template('loggedin.html', user_pic_url=pic.data['data']['url'], user_name=me['name'])
    else:
        return render_template('loggedout.html')

app.jinja_env.globals.update(user_area=user_area)

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
    return render_no_search_template('index.html', form=search_field, landing_title="Etymograph", body_class="index")

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
        response = json.dumps(results)
        return response

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=False, **kwargs)

def render_no_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=True, **kwargs)

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
            errDesc = str(e)
            response = json.jsonify({'error': errDesc})
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
        me = get_user()
        authorized = False
        if me is not None:
            authorized = True
        response = render_search_template('info.html',word_properties=info, body_class="info", word_id=word_id, authorized=authorized)
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
            del word_data['lang_name']
            # add the word to the database
            word = Word(word_data)
            word_id = model.add_word(me, word)
            return redirect('/{}'.format(word_id))

        langs = sorted([model.names[code] for code in model.names])
        lang_lookup = {}
        for code in model.names:
            lang_lookup[model.names[code]] = code
        return render_search_template('addword.html', form=form, langs=langs, lang_lookup=lang_lookup)
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

        try:
            word = Word(word_id, model.graph)
            root = Word(root_id, model.graph)
        except AttributeError:
            abort(400)

        try:
            model.add_relationship(me, word, root, source=source)
        except AttributeError:
            abort(400)
        next_url = request.args.get('next') or '/{}'.format(word_id)
        return redirect(next_url)
    else:
        abort(403)

@app.route('/edit/rel/<int:root_id>/<int:desc_id>', methods=['GET','POST'])
def edit_rel(root_id, desc_id):
    me = get_user()
    if me is not None:
        form = EditRelForm(request.form)
        #get dicts of info about this relationship
        try:
            (root, rel, desc) = model.get_rel(root_id, desc_id)
        except model.RelNotFoundException:
            abort(404)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            source = form.source.data
            # edit the relationship the database TODO
            user = get_user()
            model.edit_rel_source(user, root_id, desc_id, source)
            next_url = '/{}'.format(root_id)
            return redirect(next_url)

        my_URL = url_for('edit_rel', root_id=root_id, desc_id=desc_id)
        return render_search_template('edit_rel.html', form=form, root=root, rel=rel, desc=desc, my_URL=my_URL)
    else:
        abort(403)

@app.route('/<int:word_id>')
def show_graph(word_id):
    try:
        word_roots = model.roots(word_id)
        word_descs = model.descs(word_id)
        search_field = SearchForm()
        authorized = False
        me = get_user()
        if me is not None:
            authorized = True
        return render_search_template('graph.html', roots=word_roots, descs=word_descs,
                form=AddRootForm(), body_class="graph")
    except model.WordNotFoundException:
        abort(404)

@app.route('/flagged')
def show_flagged():
    words = model.get_flagged_words()
    rels = model.get_flagged_rels()
    return render_search_template('flagged.html', words=words, rels=rels)

@app.route('/flag/<int:word_id>', methods=['POST'])
def flag(word_id):
    if not word_id:
        abort(404) # cannot flag non-existent words.
    me = get_user()
    if me is not None:
        try:
            if me['id']:
                model.flag(me['id'], word_id)
            return_url = request.args.get('next')
            return redirect(return_url)
        except modelWordNotFoundException:
            abort(404)

@app.route('/flag/rel/<int:root_id>/<int:desc_id>', methods=['POST'])
def flag_rel(root_id, desc_id):
    if not root_id or not desc_id:
        abort(404) # cannot flag non-existent relations.
    me = get_user()
    if me is not None:
        try:
            if me['id']:
                model.flag_relationship(me['id'], root_id, desc_id)
            return_url = request.args.get('next') or '/edit/rel/'+str(root_id)+'/'+str(desc_id)
            return redirect(return_url)
        except model.WordNotFoundException:
            abort(404)


@app.route('/about')
def about():
    return render_search_template('about.html')

@app.route('/api')
def api_doc():
    return render_search_template('api.html')

if __name__ == '__main__':
    app.run(debug=True)
