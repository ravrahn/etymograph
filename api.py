from py2neo import *
from word import *
from flask import Flask, request, json
from io import StringIO
app = Flask(__name__)
graph = Graph()

@app.route('/search')
def search(): # ET-5
	if 'q' in request.args:
		return 'hello {}'.format(request.args['q'])
	else:
		return 'hello world'

@app.route('/<word>/roots')
def roots(word): # ET-6
    for record in graph.cypher.execute("MATCH (n)-[r:root*..depth]->() WHERE id(n) = id RETURN n"):
 
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
