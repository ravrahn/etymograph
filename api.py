from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for
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
    frontend_request = False
    if not request.headers['Accept'] == 'application/json':
        frontend_request = True

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

    if frontend_request:
        words = [w for w in results.values()]
        return render_template('results.html', search_str=search_str.capitalize(), results=words)
    else:
        response = json.jsonify(results)
        response.status_code = 200
        return response


@app.route('/<int:word>/roots')
def roots(word): # ET-6
    q = ("MATCH (n)-[r:root*..{}]->() WHERE id(n) = {} RETURN n")
    if 'depth' in request.args:
        depth = request.args['depth']
        return 'hello {}'.format(request.args['q'])
    else:
        depth = ''
        execution = graph.cypher.execute(q.format(depth,word))
        execution = json.jsonify
    try:
        node = graph.node(word)
        node.properties["id"] = word
    except GraphError:
        errNum  = 1234
        errRoot = ("errrror")
        response = json.jsonify({'error':errNum,'description':errRoot})
        response.status_code = 404
        return "bad"

    return str(node.properties)
   
    
@app.route('/<word>/descs')
def descs(word): # ET-7
    # Check the word ID is valid
    try:
        # Get the node
        node = graph.node(word)

        # Adding the ID of the word into the hash
        node.properties["id"] = word
    except GraphError:
        errNum  = 1234 # placeholder error num. TODO: change
        errDesc = ("blah blah")
        response = json.jsonify({'error': errNum, 'description': errDesc})
        response.status_code = 404 # File not found
        return "bad"

    # Get it's decendants

    # Put those decendants into the node.properties hash
    # e.g. node.properties

    return str(node.properties)

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
            # display file not found page TODO make template for this
            error_page = render_template('info.html', word_properties={'orig_form':'File not found'})
            return error_page, 404       
        
    # No problems encountered
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
    word_roots = rootstest(word_id)
    word_descs = descstest(word_id)
    return render_template('graph.html', roots=word_roots, descs=word_descs)



@app.route('/rootstest')
def rootstest(word_id):
    with open('rootstest.json') as roots:
        return roots.read()

@app.route('/descstest')
def descstest(word_id):
    with open('descstest.json') as descs:
        return descs.read()


if __name__ == '__main__':
    app.run(debug=True)
