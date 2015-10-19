from py2neo import *
from word import *
import json, time
from difflib import SequenceMatcher
from flask import abort

graph = Graph('http://db.etymograph.com/db/data')
# Language codes from data from www.sil.org/iso639-3/
lang_code_file = 'lang_names.json'
with open(lang_code_file, 'r') as f:
    names = json.load(f)

class WordNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
        
class RelNotFoundException(Exception):
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
    node = get_node_safe(word_id)
    info = node.properties
    # Adds a human-readable name to the information
    if 'language' in info:
        try:
            info['lang_name'] = lang_decode(info['language'])
        except KeyError:
            pass
    return info

def get_rel(root_id, desc_id):
    '''
    This function should return info on a relationship
    between the nodes of given IDs, if it exists.
    Returns dicts of info on the root, the relationship and the desc, 
    in that order
    '''
    # get root
    root = get_node_safe(root_id)
    root_info = root.properties
    # Adds a human-readable name to the information
    if 'language' in root_info:
        try:
            root_info['lang_name'] = lang_decode(root_info['language'])
        except KeyError:
            pass
    # get desc
    desc = get_node_safe(desc_id)
    desc_info = desc.properties
    # Adds a human-readable name to the information
    if 'language' in desc_info:
        try:
            desc_info['lang_name'] = lang_decode(desc_info['language'])
        except KeyError:
            pass       
    # note that the root relationship goes from desc -> root
    rel = graph.match_one(start_node=desc, rel_type="root", end_node=root)
    if(rel == None):
        raise RelNotFoundException("The word with ID {} is not a root of the word with ID {}".format(root_id, desc_id))
    rel_info = rel.properties
    
    return (root_info, rel_info, desc_info)


def search(query):
    '''
    This function should return a list of tuples of the form
    (id, properties) for search results given a string to search for.
    '''

    if not query:
        abort(400)

    cypher_query = "MATCH (n) WHERE n.orig_form =~ {sub_str} RETURN n,id(n)"
    params = { 'sub_str': '(?i).*{}.*'.format(query) }

    results = {}
    try:
        results = {uid: node.properties for (node, uid) in graph.cypher.execute(cypher_query, params)}
    except GraphError:
        return [(-1, {'error': 'Invalid request'})]

    def sort_alpha(tup):
        k, v = tup
        m = SequenceMatcher(None, v['orig_form'], query)
        ratio = m.quick_ratio() + 0.0001 # cheap hack to avoid /0 errors
        return 1/ratio

    results = sorted(results.items(), key=sort_alpha)

    return results


def add_word(user, word):
    ''' Add a word to the database, given a user and the word to add '''
    word.get_node(graph)
    user_node = graph.find_one('User', property_key='id', property_value=user['id'])
    creation_time = int(time.time())
    created = Relationship(user_node, 'created', word.node, time=creation_time)
    graph.create(created)

    return word.id

def add_relationship(user, word, root, **kwargs):
    ''' Add a relationship to the database, given the user and two words
    Give the relationship arbitrary properties described in **kwargs'''
    word.get_node(graph)
    root.get_node(graph)
    rel = Relationship(word.node, 'root', root.node, **kwargs)
    graph.create(rel)
    creation_time = int(time.time())
    user_node = graph.find_one('User', property_key='id', property_value=user['id'])
    created = Relationship(user_node, 'created_rel', word.node, time=creation_time, root=root.id)
    graph.create(created)

    return word.id

def add_user(user):
    user_node = graph.merge_one('User', property_key='id', property_value=user['id'])
    user_node.push()

#TODO refactor so that this can be used to edit arbitrary rel properties
def edit_rel_source(user, root_id, desc_id, new_source):
    ''' changes the source of a relationship in the database'''
    root = get_node_safe(root_id)
    desc = get_node_safe(desc_id)
    # note that the root relationship goes from desc -> root
    rel = graph.match_one(start_node=desc, rel_type="root", end_node=root)
    if(rel == None):
        raise RelNotFoundException("The word with ID {} is not a root of the word with ID {}".format(root_id, desc_id))
    rel['source'] = new_source
    # could add info about the editing user here
    rel.push()
    
    
def get_node_safe(node_id):
    try:
        node = graph.node(node_id)
        node.pull()
        return node
    except GraphError:
        raise WordNotFoundException("Word with ID {} not found".format(root_id))

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
        raise KeyError("Could not find a language with the code '{}'".format(code))


def invalid_query(query):
    """
    Validates a query for blank input and numbers.
    """
    if not query: # blank query
        return True

    try: # Invalid if no exception thrown.
        float(query) or int(query)
        return True
    except ValueError:
        return False
