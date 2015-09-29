from py2neo import *
from word import *
from flask import Flask, request, json, render_template
from io import StringIO

from forms import SearchForm

app = Flask(__name__)
app.config.from_object('config')
graph = Graph()

# authenticate('localhost:7474', "neo4j", "__insert-password-here__")
authenticate('localhost:7474', "neo4j", "etymograph")


"""
Validates a query
Returns True if the query is blank or contains unwanted cypher code.
"""
def unsafe_query(query):
    invalid_substrs = \
            [':server', 'password', 'CREATE', 'DELETE', 'REMOVE', 'MATCH', 'RETURN', 'SET', 'MERGE']
    if not query: # blank query
        return True
    else:
        for unwanted in invalid_substrs:
            if unwanted in query:
                return True
    return False


@app.route('/results')
def show_results(search_str):
    # TODO
    pass


@app.route('/index.html')
@app.route('/')
def index():
    search_field = SearchForm()
    if search_field.validate_on_submit():
        #TODO make this point to results
        return redirect(url_for('search', q=search_field.query.data))
    return render_template('index.html', form=search_field, landing_title="Etymograph")


"""
Search for all words that match a particular substring
usage: /search?q=<string>
"""
@app.route('/search', methods=["GET", "POST"])
def search(): # ET-5
    search_str = ''
    if request.args['q']:
        search_str = request.args['q']
    else:
        search_str = request.form['query']

    try:
        if 'q' in request.args:
            search_str = request.args['q']

            if unsafe_query(search_str):
                return "Bad request."

            # TODO Validate against queries containing regex?
            query = "MATCH (n) WHERE n.orig_form =~ '.*{}.*' RETURN n,id(n)".format(search_str)
            results = {}
            for record in graph.cypher.execute(query):
                uid = record[1]
                results[uid] = record[0].properties
            response = json.jsonify(results)
            response.status_code = 200
        else:
            return "Bad request."
    except GraphError:
        errNum  = 1234 # placeholder error num. TODO: change
        errDesc = "Error accessing database"
        response = json.jsonify({'error': errNum, 'description': errDesc})
        response.status_code = 404
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
    return 'hello {}'.format(word)


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


if __name__ == '__main__':
    app.run(debug=True)
