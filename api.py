from py2neo import *
from word import *
from flask import Flask, request, json, render_template, redirect, url_for
from io import StringIO

from forms import SearchForm

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


@app.route('/<word>/roots')
def roots(word): # ET-6
    q = ("MATCH (n)-[r:root*..{}]->() WHERE id(n) = {} RETURN n")
    if 'q' in request.args:
        return 'hello {}'.format(request.args['q'])
    else:
        query = ''

    #return 'hello {}'.format(word)


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

@app.route('/<int:wordID>/info')
def info(wordID): # ET-20
    try:
        node = graph.node(wordID)
        # pull the latest version of the node from the server (needed?)
        node.pull();
        # Convert word data to JSON and wrap in a Flask response
        response = json.jsonify(node.properties)
        response.status_code = 200 # OK
    except GraphError:
        errNum  = 1234 # placeholder error num. TODO: change
        errDesc = "Word with ID {} could not be found".format(wordID)
        response = json.jsonify({'error': errNum, 'description': errDesc})
        response.status_code = 404 # File not found
    return response


@app.route('/<int:word_id>')
def show_graph(word_id):
    roots = rootstest(word_id)
    descs = descstest(word_id)
    return render_template('graph.html', roots=roots, descs=descs)



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
