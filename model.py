from py2neo import *
from word import *

graph = Graph('http://etymograph.com:7474/db/data')

class WordNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def roots(word_id, depth):
	'''
	This function should return a recursive dictionary of roots
	given a word's id and a depth.
	'''
	return {}

def descs(word_id, depth):
	'''
	This function should return a recursive dictionary of descendants
	given a word's id and a depth.
	'''
	return {}

def info(word_id):
    '''
    This function should return a dictionary of information about a word
    given a word's id.
    '''
    try:
        node = graph.node(word_id)
        # pull the latest version of the node from the server (needed?)
        node.pull();        
    except GraphError:
        raise WordNotFoundException("Word with ID {} not found".format(word_id))
    return node.properties

def search(query):
	'''
	This function should return an array of search results given
	a string to search for.
	'''
	return []
