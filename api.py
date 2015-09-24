from py2neo import *
from word import *
from flask import Flask
app = Flask(__name__)
graph = Graph()

@app.route('/search/<string>')
def search(string): # ET-5
	return "hello {}".format(string)

@app.route('/roots/<word>')
def roots(word): # ET-6
	return "hello {}".format(word)

@app.route('/descs/<word>')
def descs(word): # ET-7
	return "hello {}".format(word)

@app.route('/info/<word>')
def info(word): # ET-20
	return "hello {}".format(word)

if __name__ == '__main__':
	app.run(debug=True)