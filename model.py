from py2neo import *
from word import *
import json

graph = Graph('http://etymograph.com:7474/db/data')
# Language codes from data from www.sil.org/iso639-3/
lang_code_file = 'lang_names.json'
with open(lang_code_file, 'r') as f:
    names = json.load(f)

class WordNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def roots(word_id, depth=None):
	'''
	This function should return a recursive dictionary of roots
	given a word's id and a depth.
	'''
	word_info = info(word_id)
	word_info['id'] = word_id
	word_info['roots'] = []

	if depth == 0:
		return word_info

	query = 'MATCH (n)-[r:root]->(e) WHERE id(n) = {id} RETURN id(e)'

	results = graph.cypher.execute(query, {'id': word_id})

	for result in results:
		node_id = result[0]
		if depth is not None:
			new_depth = depth - 1
		else:
			new_depth = None
		word_info['roots'].append(roots(node_id, depth=new_depth))

	return word_info

def descs(word_id, depth=None):
	'''
	This function should return a recursive dictionary of descendants
	given a word's id and a depth.
	'''
	word_info = info(word_id)
	word_info['id'] = word_id
	word_info['descs'] = []

	if depth == 0:
		return word_info

	query = 'MATCH (e)-[r:root]->(n) WHERE id(n) = {id} RETURN id(e)'

	results = graph.cypher.execute(query, {'id': word_id})

	for result in results:
		node_id = result[0]
		if depth is not None:
			new_depth = depth - 1
		else:
			new_depth = None
		word_info['descs'].append(descs(node_id, depth=new_depth))

	return word_info

def info(word_id):
    '''
    This function should return a dictionary of information about a word
    given a word's id.
    '''
    try:
        node = graph.node(word_id)
        node.pull();
    except GraphError:
        raise WordNotFoundException("Word with ID {} not found".format(word_id))
    info = node.properties
    # Adds a human-readable name to the information
    if 'language' in info:
        try:
            info['lang_name'] = lang_decode(info['language'])
        except KeyError:
            pass
    return info

def search(query):
    '''
    This function should return a list of tuples of the form
    (id, properties) for search results given a string to search for.
    '''

    #TODO Remove?
    if unsafe_query(query):
        return [(-1, {'error': 'Invalid request'})]

    cypher_query = "MATCH (n) WHERE n.orig_form =~ {sub_str} RETURN n,id(n)"
    params = { 'sub_str': '.*{}.*'.format(query) }

    results = {}
    try:
        results = {uid: node.properties for (node, uid) in graph.cypher.execute(cypher_query, params)}
    except GraphError:
        return [(-1, {'error': 'Invalid request'})]

    def sort_alpha(tup):
        k, v = tup
        return v['orig_form']

    results = sorted(results.items(), key=sort_alpha)
    print(results)

    return results

def lang_decode(code):
    '''
    Given an ISO 639-3 language code,
    returns the name of the language with that code
    '''
    # with open(lang_code_file, 'r') as f:
    #     names = json.load(f)
    if code in names:
        return names[code]
    else:
        raise KeyError("Could not find a language with the code '{}'").format(code)


def descstest(word_id):
    with open('descstest.json') as descs:
        return descs.read()


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
