# -*- coding: utf-8 -*-
from flask import Flask, request, json, render_template, redirect, url_for, abort, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from io import StringIO
from forms import *
import collections
from difflib import SequenceMatcher
from flask_oauthlib.client import OAuth, OAuthException

import model

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

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

    me_check = model.get_user(me.data['id'])
    if not me_check.first():
        me_db = model.User('facebook', me.data['id'])
        db.session.add(me_db)
        db.session.commit()

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
    user_db = model.User.query.filter_by(token=user['id']).first()
    results = [word.info() for word in user_db.created_words]
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
    '''
    returns true if the current request has a JSON application type, false otherwise.
    This helper function from http://flask.pocoo.org/snippets/45/
    '''
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=False, **kwargs)

def render_no_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=True, **kwargs)

@app.route('/index.html') # ET-19
@app.route('/')
def index():
    search_field = SearchForm()
    return render_no_search_template('index.html', form=search_field, landing_title="Etymograph", body_class="index")

@app.route('/search')
def search(): # ET-5, ET-19
    '''
    Search for all words that match a particular substring
    usage: /search?q=<string> or frontend search bar
    '''
    query = request.args['q']
    results = model.Word.query.filter(model.Word.orig_form.like('%' + query + '%')).all()
    
    results = [word.info() for word in results]

    def sort_alpha(word):
        m = SequenceMatcher(None, word['orig_form'], query)
        ratio = m.quick_ratio() + 0.0001 # cheap hack to avoid /0 errors
        return 1/ratio

    results = sorted(results, key=sort_alpha)

    if not request_wants_json():
        search_field = SearchForm()
        return render_search_template('results.html',
            form=search_field,
            search_str=query.capitalize(),
            results=results, body_class="search")
    else:
        response = json.dumps(results)
        return response

@app.route('/<int:word_id>/roots')
def roots(word_id): # ET-6
    if 'depth' in request.args:
        depth = int(request.args['depth'])
        if depth < 0:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    word = model.get_word(word_id)
    if word is not None:
        response = json.jsonify(word.get_roots(depth=depth))
        response.status_code = 200
    else:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response


@app.route('/<int:word_id>/descs')
def descs(word_id): # ET-7
    if 'depth' in request.args:
        depth = int(request.args['depth'])
        if depth < 0:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    word = model.get_word(word_id)
    if word is not None:
        response = json.jsonify(word.get_descs(depth=depth))
        response.status_code = 200
    else:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response

@app.route('/<int:word_id>/info')
def info(word_id): # ET-20
    info = model.get_word(word_id).info()
    if info is None:
        errDesc = str(e)
        response = json.jsonify({'error': errDesc})
        response.status_code = 404 #file not found
        return response

    # Convert word data to JSON and wrap in a Flask response
    response = json.jsonify(info)
    response.status_code = 200 # OK
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
            word = model.Word(model.get_user(me['id']),
                word_data['orig_form'],
                word_data['language'],
                definition=word_data['definition'],
                latin_form=word_data['latin_form'],
                ipa_form=word_data['ipa_form'])
            model.db.session.add(word)
            model.db.session.commit()
            return redirect('/{}'.format(word.id))

        langs = sorted([model.names[code] for code in model.names])
        lang_lookup = {}
        for code in model.names:
            lang_lookup[model.names[code]] = code
        return render_search_template('addword.html', form=form, langs=langs, lang_lookup=lang_lookup)
    else:
        abort(403)

@app.route('/edit/word/<int:word_id>', methods=['GET', 'POST'])
def edit_word(word_id):
    me = get_user()
    if me is not None:
        form = EditWordForm(request.form)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            word_data = form.data
            del word_data['lang_name']
            # edit the word in the database
            word = model.get_word(word_id)
            word.orig_form = word_data['orig_form']
            word.language = word_data['language']
            word.definition = word_data['definition']
            word.ipa_form = word_data['ipa_form']
            word.latin_form = word_data['latin_form']
            model.db.session.commit()
            return redirect('/{}'.format(word_id))

        langs = sorted([model.names[code] for code in model.names])
        lang_lookup = {}
        for code in model.names:
            lang_lookup[model.names[code]] = code
        word = model.get_word(word_id).info()
        return render_search_template('editword.html', form=form, langs=langs, lang_lookup=lang_lookup, word=word)
    else:
        abort(403)


@app.route('/add/root', methods=['POST'])
def add_root():
    me = get_user()
    if me is not None:
        form = AddRootForm(request.form)
        word_id = int(form.word_id.data)
        root_id = int(form.root_id.data)
        source = form.source.data

        word = model.get_word(word_id)
        root = model.get_word(root_id)

        if word is not None and root is not None:
            rel = model.Rel(model.get_user(me['id']), root, word, source)
            model.db.session.add(rel)
            model.db.session.commit()
        else:
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
        rel = model.Rel.query.filter_by(root_id=root_id, desc_id=desc_id).first()
        if rel is None:
            abort(404)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            source = form.source.data
            # edit the relationship the database 
            rel.source = source
            model.db.session.commit()
            next_url = '/{}'.format(root_id)
            return redirect(next_url)

        my_URL = url_for('edit_rel', root_id=root_id, desc_id=desc_id)
        return render_search_template('edit_rel.html', form=form, root=rel.root.info(), rel=rel.info(), desc=rel.desc.info(), my_URL=my_URL)
    else:
        abort(403)

@app.route('/<int:word_id>')
def show_graph(word_id):
    word = model.get_word(word_id)
    word_roots = word.get_roots()
    word_descs = word.get_descs()

    if word is None:
        abort(404)
    else:
        return render_search_template('graph.html', roots=word_roots, descs=word_descs,
            form=AddRootForm(), body_class="graph", add_root_search=SearchForm())

@app.route('/flagged')
def show_flagged():
    words = [flag.word.info() for flag in model.WordFlag.query.all()]
    rels = [flag.rel.info() for flag in model.RelFlag.query.all()]
    return render_search_template('flagged.html', words=words, rels=rels)

@app.route('/flag/<int:word_id>', methods=['POST'])
def flag(word_id):
    word = model.get_word(word_id)
    me = get_user()
    if me is not None and word is not None:
        me_db = model.get_user(me['id'])
        flag = model.WordFlag(me_db, word)
        model.db.session.add(flag)
        model.db.session.commit()
        return_url = request.args.get('next')
        return redirect(return_url)
    else:
        abort(404)

@app.route('/flag/rel/<int:root_id>/<int:desc_id>', methods=['POST'])
def flag_rel(root_id, desc_id):
    if not root_id or not desc_id:
        abort(404) # cannot flag non-existent relations.
    rel = model.Rel.query.filter_by(root_id=root_id, desc_id=desc_id).first()
    me = get_user()
    if me is not None and rel is not None:
        me_db = model.get_user(me['id'])
        flag = model.RelFlag(me_db, rel)
        model.db.session.add(flag)
        model.db.session.commit()
        return_url = request.args.get('next') or '/edit/rel/'+str(root_id)+'/'+str(desc_id)
        return redirect(return_url)
    else:
        abort(404)


@app.route('/about')
def about():
    return render_search_template('about.html')

@app.route('/api')
def api_doc():
    return render_search_template('api.html')

if __name__ == '__main__':
    app.run(debug=True)
