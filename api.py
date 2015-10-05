from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for, abort
from io import StringIO

from forms import SearchForm

import model

app = Flask(__name__)
app.config.from_object('config')
graph = Graph('http://etymograph.com:7474/db/data')

#TODO remove?
"""
Validates a query
Returns True if the query is blank or contains unwanted cypher code.
"""
def unsafe_query(query):
    # FIXME
    invalid_substrs = \
            [':server', 'password', 'CREATE', 'DELETE', 'REMOVE', 'MATCH', 'RETURN', 'SET', 'MERGE']
    if not query: # blank query
        return True
    else:
        for unwanted in invalid_substrs:
            if unwanted in query:
                return True
    return False

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
    if search_field.validate_on_submit():
        return redirect(url_for('search', q=search_field.query.data))
    return render_template('index.html', form=search_field, landing_title="Etymograph")


"""
Search for all words that match a particular substring
usage: /search?q=<string> or frontend search bar
"""
@app.route('/search')
def search(): # ET-5, ET-19
    search_str = request.args['q']

    #TODO Remove?
    if unsafe_query(search_str):
        return "Bad request."

    query = "MATCH (n) WHERE n.orig_form =~ {sub_str} RETURN n,id(n)"
    params = { 'sub_str': '.*{}.*'.format(search_str) }

    results = {}
    try:
        results = {uid: node.properties for (node, uid) in graph.cypher.execute(query, params)}
    except GraphError:
        errDesc = "Error accessing database"
        response = json.jsonify({'error': errDesc})
        response.status_code = 404

    if not request_wants_json():
        return render_template('results.html', search_str=search_str.capitalize(), results=results)
    else:
        response = json.jsonify(results)
        response.status_code = 200
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
   
    
@app.route('/<word>/descs')
def descs(word): # ET-7
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
