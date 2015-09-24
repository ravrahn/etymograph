from py2neo import *

class Word:
    '''Representation of a word
    Properties:
     - lang: language of the word
     - orig_form: original form (unicode) of the word.
     - eng_form: latin-alphabet transliteration of the word.
     - ipa_form: IPA transcription of the word
     - definition: definition of the word'''

    def __init__(self, name, lang, pronunciation=None, definition=None, latin=None):
        self.node = None
        self.props = {}
        self.props['orig_form'] = name.strip().replace('"', '\\"')
        self.props['language'] = lang.strip()

        if pronunciation not None:
            self.props['ipa_form'] = pronunciation
        if definition not None:
            self.props['definition'] = definition
        if latin not None:
            self.props['eng_form'] = latin
        elif name :
            self.props['eng_form'] = name

    def __init__(self, node):
        self.node = node
        self.props = node.properties

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

        cond = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in self.props.items()]) + '}'
        query = 'MERGE (n:Word {}) RETURN n'
        query = query.format(cond)
        results = graph.cypher.execute(query)

        if results:
            self.node = results[0]['n']
        else:
            self.node = Node('Word', name=self.props['name'], lang=self.props['lang'])

        return self.node

def add_relationship(graph, start, end, rel):

    condStart = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in start.props.items()]) + '}'
    condEnd = '{' + ', '.join(['{}: "{}"'.format(prop, value) for prop, value in end.props.items()]) + '}'
    query = 'MATCH (a:Word {}),(b:Word {}) MERGE (a)-[r:{} {source:"etymwn"}]-(b) RETURN r'
    query = query.format(condStart, condEnd, rel)

    graph.cypher.execute(query)