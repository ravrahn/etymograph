from py2neo import *
from word import *
from flask import Flask, request
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
	return 'hello {}'.format(word)

@app.route('/<word>/descs')
def descs(word): # ET-7
	return 'hello {}'.format(word)

@app.route('/<word>/info')
def info(word): # ET-20
	return 'hello {}'.format(word)

if __name__ == '__main__':
	app.run(debug=True)