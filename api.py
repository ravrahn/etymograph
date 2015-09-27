from py2neo import *
from word import *
from flask import Flask, request, json
from io import StringIO
app = Flask(__name__)
graph = Graph()

# authenticate('localhost:7474', "neo4j", "__insert-password-here__") 

@app.route('/search')
def search(): # ET-5
    # TODO Add try-catch blocks like info()
    if 'q' in request.args:
        search_str = request.args['q']
        query = "MATCH (n) WHERE n.orig_form =~ '.*{}.*' RETURN n".format(search_str)
        results = {}
        record_list = graph.cypher.execute(query);
        subgraph = record_list.to_subgraph();
        for node in subgraph.nodes:
            uid = node.properties['ID']
            props = dict((k, v) for k, v in node.properties.items() if k != 'ID')
            results[uid] = props
        response = json.jsonify(results)
        response.status_code = 200
        return response
    else:
        return "Malformed search request."

@app.route('/<word>/roots')
def roots(word): # ET-6
    for record in graph.cypher.execute("MATCH (n <id>)-[r:root*1..<number>]->() RETURN n"):
        return 'hello {}'.format(word)

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
