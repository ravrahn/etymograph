from py2neo import *
from word import *
import json, time
from difflib import SequenceMatcher
from flask import abort

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

    return dict(word_info)

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

    return dict(word_info)

def info(word_id):
    '''
    This function should return a dictionary of information about a word
    given a word's id.
    '''
    node = get_node_safe(word_id)
    info = node.properties
    info['id'] = word_id
    # Adds a human-readable name to the information
    if 'language' in info:
        try:
            info['lang_name'] = lang_decode(info['language'])
        except KeyError:
            pass

    flag_count_query = 'MATCH (:User)-[f:flagged]->(n:Word) WHERE id(n) = {id} RETURN COUNT(f)'
    info['flag_count'] = graph.cypher.execute(flag_count_query, {'id': word_id})[0][0]

    return dict(info)

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
    root_info['id'] = root_id
    # get desc
    desc = get_node_safe(desc_id)
    desc_info = desc.properties
    # Adds a human-readable name to the information
    if 'language' in desc_info:
        try:
            desc_info['lang_name'] = lang_decode(desc_info['language'])
        except KeyError:
            pass
    desc_info['id'] = desc_id
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

    cypher_query = "MATCH (n:Word) WHERE n.orig_form =~ {sub_str} RETURN id(n)"
    params = { 'sub_str': '(?i).*{}.*'.format(query) }

    results = []
    try:
        for node in graph.cypher.execute(cypher_query, params):
            uid = node[0]
            result = info(uid)
            results.append(result)
    except GraphError:
        return [(-1, {'error': 'Invalid request'})]

    def sort_alpha(word):
        m = SequenceMatcher(None, word['orig_form'], query)
        ratio = m.quick_ratio() + 0.0001 # cheap hack to avoid /0 errors
        return 1/ratio

    results = sorted(results, key=sort_alpha)

    return results


def add_word(user, word):
    ''' Add a word to the database, given a user and the word to add '''
    word.get_node(graph)
    user_node = graph.find_one('User', property_key='id', property_value=user['id'])
    creation_time = int(time.time())
    created = Relationship(user_node, 'created', word.node, time=creation_time)
    graph.create(created)

    return word.id

def user_added_word(user):
    query = 'MATCH (u:User)-[:created]->(n:Word) WHERE u.id = {User} RETURN id(n)' 
    results = graph.cypher.execute(query, {'User': user })
    results2 = []
    for result in results:
        word_id = result[0]
        word_info = info(word_id)
        results2.append(word_info)
    return results2

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

def edit_word(user_id, word_id, new_properties):
    """
    Edits the properties of a word with given id.
    Note that other properties are not changed
    """
    query = "MATCH (u:User), (w:Word) WHERE u.id = {user_id} AND id(w) = {word_id} "
    keys = sorted(new_properties.keys())
    for key in keys:
        query += 'SET w.{} = "{}" '.format(key, new_properties[key])
    query += "CREATE (u)-[r:edited_word {time: {created_time} }]->(w)"
    query += "RETURN w"
    results = graph.cypher.execute(query, {'user_id': str(user_id), 'word_id': int(word_id), 'created_time': int(time.time())})
    if len(results) == 0:
        raise WordNotFoundException("Word with ID {} not found".format(word_id))


def get_flagged_words():
    results = graph.cypher.execute('MATCH (:User)-[f:flagged]->(n:Word) RETURN id(n),COUNT(f)')

    words = []

    for result in results:
        word = info(result[0])
        words.append(word)

    return words

def get_flagged_rels():
    results = graph.cypher.execute('MATCH (:User)-[f:flagged_rel]->(d:Word)-[:root]->(r:Word) WHERE id(r) = f.root RETURN id(r),id(d),COUNT(f)')

    rels = []
    for result in results:
        root = info(result[0])
        desc = info(result[1])

        rel = { 
            'root': root,
            'desc': desc,
            'flag_count': result[2]
            }
        rels.append(rel)

    return rels


def flag(user_id, word_id):
    """
    Creates a flag relationship between user and word
    """
    query = """MATCH (u:User),(w:Word) WHERE u.id = {user_id} AND id(w) = {word_id} MERGE (u)-[f:flagged]->(w) RETURN f"""
    graph.cypher.execute(query, {'user_id': str(user_id), 'word_id': int(word_id)})

def flag_relationship(user_id, root_id, desc_id):
    """
    Creates a flagged_rel relationship between user and decs of relationship
    """
    query = """MATCH (u:User), (r:Word), (d:Word) 
            WHERE u.id = {user_id} AND id(r) = {root_id} AND id(d) = {desc_id} 
            MERGE (u)-[f:flagged_rel {root:{root_id}, desc:{desc_id}}]->(d) 
            ON CREATE SET f.flag_count = 1
            RETURN f"""
    graph.cypher.execute(query, {'user_id': str(user_id), 'root_id': int(root_id), 'desc_id': int(desc_id)})
    

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
    # TODO could add info about the editing user here
    rel.push()


def get_node_safe(node_id):
    try:
        node = graph.node(node_id)
        node.pull()
        return node
    except GraphError:
        raise WordNotFoundException("Word with ID {} not found".format(node_id))

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

