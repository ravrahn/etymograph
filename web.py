from flask import Blueprint, abort
from forms import *

from helpers import *
import model

web = Blueprint('web', __name__)

@web.route('/index.html') # ET-19
@web.route('/')
def index():
    search_field = SearchForm()
    return render_no_search_template('index.html', form=search_field, landing_title="Etymograph", body_class="index", title='')

@web.route('/<int:word_id>')
def show_graph(word_id):
    word = model.Word.query.get(word_id)
    word_roots = word.get_roots()
    word_descs = word.get_descs()

    if word is None:
        abort(404)
    else:
        return render_search_template('graph.html', roots=word_roots, descs=word_descs,
            form=AddRootForm(), body_class="graph", add_root_search=SearchForm(), title=word.orig_form)

@web.route('/flagged')
def show_flagged():
    words = [flag.word.info() for flag in model.WordFlag.query.all()]
    rels = [flag.rel.info() for flag in model.RelFlag.query.all()]
    return render_search_template('flagged.html', words=words, rels=rels, title='Flagged')

@web.route('/about')
def about():
    return render_search_template('about.html', title='About')

@web.route('/api')
def api_doc():
    return render_search_template('api.html', title='API')