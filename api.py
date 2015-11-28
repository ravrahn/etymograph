from flask import Blueprint, request, json
from forms import *
from difflib import SequenceMatcher

from helpers import *
import model

api = Blueprint('api', __name__)

@api.route('/search')
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
            search_str=query,
            results=results, body_class="search", title='Results for {}'.format(query))
    else:
        response = json.dumps(results)
        return response

@api.route('/<int:word_id>/roots')
def roots(word_id): # ET-6
    if 'depth' in request.args:
        depth = int(request.args['depth'])
        if depth < 0:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    word = model.Word.query.get(word_id)
    if word is not None:
        response = json.jsonify(word.get_roots(depth=depth))
        response.status_code = 200
    else:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response


@api.route('/<int:word_id>/descs')
def descs(word_id): # ET-7
    if 'depth' in request.args:
        depth = int(request.args['depth'])
        if depth < 0:
            response = json.jsonify({ 'error': 'Invalid depth' })
            response.status_code = 400
            return response
    else:
        depth = None

    word = model.Word.query.get(word_id)
    if word is not None:
        response = json.jsonify(word.get_descs(depth=depth))
        response.status_code = 200
    else:
        response = json.jsonify({ 'error': 'Word not found' })
        response.status_code = 404

    return response

@api.route('/<int:word_id>/info')
def info(word_id): # ET-20
    info = model.Word.query.get(word_id).info()
    if info is None:
        errDesc = str(e)
        response = json.jsonify({'error': errDesc})
        response.status_code = 404 #file not found
        return response

    # Convert word data to JSON and wrap in a Flask response
    response = json.jsonify(info)
    response.status_code = 200 # OK
    return response