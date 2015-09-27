from py2neo import *
from word import *
from flask import Flask, request, json
from io import StringIO
app = Flask(__name__)
graph = Graph()

# authenticate('localhost:7474', "neo4j", "__insert-password-here__") 


def unsafe_query(query):
    invalid_substrs = ['CREATE', 'DELETE', 'REMOVE', 'MATCH', 'RETURN', 'SET', 'MERGE']
    if not query: # blank query
        return True
    else:
        for unwanted in invalid_substrs: # contains cypher code
            if unwanted in query: 
                return True
    return False

@app.route('/search')
def search(): # ET-5
    # TODO Add try-catch blocks like info()
    if 'q' in request.args:
        search_str = request.args['q']

        if unsafe_query(search_str): 
            return "Bad request."

        query = "MATCH (n) WHERE n.orig_form =~ '.*{}.*' RETURN n,id(n)".format(search_str)
        results = {}
        record_list = graph.cypher.execute(query);
        for record in record_list:
            uid = record[1]
            results[uid] = record[0].properties
        response = json.jsonify(results)
        response.status_code = 200
        return response
    else:
        return "Malformed search request."

@app.route('/<word>/roots')
def roots(word): # ET-6
    for record in graph.cypher.execute("MATCH (n)-[r:root*..{}]->() WHERE {}(n) = {} RETURN n"):
    if 'q' in request.args:
        return 'hello {}'.format(request.args['q'])
    else:
        emptyStrin = ''

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
