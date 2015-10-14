import string
from py2neo import *

class Word:
    '''Representation of a word
    Properties:
     - language: language of the word
     - orig_form: original form (unicode) of the word.
     - eng_form: latin-alphabet transliteration of the word.
     - ipa_form: IPA transcription of the word
     - definition: definition of the word'''
    latin = set(string.ascii_lowercase + string.ascii_uppercase + string.punctuation)

    def __init__(self, *args, **kwargs):
        if isinstance(args[0], int) and isinstance(args[1], Graph):
            self.id = args[0]
            self.node = None
        elif isinstance(args[0], Node) and isinstance(args[1], Graph):
            self.props = args[0].properties
            self.id = None
            self.node = None
            self.get_node(args[1])
        elif isinstance(args[0], dict):
            self.props = args[0]
            self.id = None
            self.node = None
        else:
            self.id = None
            self.node = None
            self.props = {}
            self.props['orig_form'] = args[0].strip().replace('"', '\\"')
            self.props['language'] = args[1].strip()

            if kwargs.get('pronunciation') is not None:
                self.props['ipa_form'] = kwargs.get('pronunciation')
            if kwargs.get('definition') is not None:
                self.props['definition'] = kwargs.get('definition')
            if kwargs.get('latin') is not None:
                self.props['eng_form'] = kwargs.get('latin')
            elif set(args[0]) <= self.latin:
                self.props['eng_form'] = args[0]

    def __eq__(self, other):
        name_matches = other.props['orig_form'] == self.props['orig_form'] 
        lang_matches = self.props['language'] == other.props['language']
        return name_matches and lang_matches # ignore the rest of the data

    def __str__(self):
        return str(self.props)

    def __hash__(self):
        return hash(str(self))

    def merge(self, graph):
        '''Add self to the graph, preserving uniqueness with a merge'''

    def get_node(self, graph):
        '''Function to create a Node out of the Word
        Returns either an existing Node from the graph,
        or a new Node'''

        if self.node is not None:
            return self.node

        if self.id is not None:
            query = 'MATCH (n:Word) WHERE id(n) = {} RETURN n,id(n)'.format(self.id)
            results = graph.cypher.execute(query)
        else:
            cond = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in self.props.items()]) + '}'
            query = 'MERGE (n:Word {}) RETURN n, id(n)'
            query = query.format(cond)
            results = graph.cypher.execute(query)

        if results:
            self.node = results[0][0]
            self.id = results[0][1]

        return self.node

def add_relationship(graph, start, end, rel):

    condStart = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in start.props.items()]) + '}'
    condEnd = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in end.props.items()]) + '}'
    query = 'MATCH (a:Word {}),(b:Word {}) MERGE (a)-[r:{} {{source:"etymwn"}}]-(b) RETURN r'
    query = query.format(condStart, condEnd, rel)

    graph.cypher.execute(query)