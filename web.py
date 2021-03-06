from flask import Blueprint, abort, redirect, url_for, request
import math

from forms import *
import helpers
import model

web = Blueprint('web', __name__)

@web.route('/index.html') # ET-19
@web.route('/')
def index():
    search_field = SearchForm()
    return helpers.render_no_search_template('index.html', form=search_field, landing_title="Etymograph", body_class="index", title='')

@web.route('/<int:word_id>')
def show_graph(word_id):
    word = model.Word.query.get(word_id)

    if word is None:
        abort(404)
    else:
        word_roots = word.get_roots()
        word_descs = word.get_descs()
        return helpers.render_search_template('graph.html', roots=word_roots, descs=word_descs,
            form=AddRootForm(), body_class="graph", add_root_search=SearchForm(), title=word.orig_form)

@web.route('/search')
def search(): # ET-5, ET-19
    '''
    Search for all words that match a particular substring
    usage: /search?q=<string> or frontend search bar
    '''
    if 'q' not in request.args or request.args['q'] == '':
        abort(400)

    query = request.args['q']

    if 'page' not in request.args:
        return redirect(url_for('web.search', q=query, page=1))
    
    page = int(request.args['page'])
    if page < 1:
        abort(400)
    per_page = 20

    results = helpers.search(query, page=page, per_page=per_page)

    return helpers.render_search_template('results.html',
        query=query,
        results=results[0],
        results_length=results[1],
        page=page,
        page_count=int(math.ceil(results[1]/per_page)),
        body_class="search",
        title='Results for {}'.format(query))

@web.route('/flagged')
def show_flagged():
    words = [flag.word.info() for flag in model.WordFlag.query.all()]
    rels = [flag.rel.info() for flag in model.RelFlag.query.all()]
    return helpers.render_search_template('flagged.html', words=words, rels=rels, title='Flagged')

@web.route('/about')
def about():
    return helpers.render_search_template('about.html', title='About')

@web.route('/api')
def api_doc():
    return helpers.render_search_template('api.html', title='API')
