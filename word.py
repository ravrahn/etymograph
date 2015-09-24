from py2neo import *

class Word:

	def __init__(self, name, lang):
		self.node = None
		self.props = {}
		self.props['name'] = name.strip().replace('"', '\\"')
		self.props['lang'] = lang.strip()

	def __eq__(self, other):
		return self.props == other.props

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
	query = 'MATCH (a:Word {}),(b:Word {}) MERGE (a)-[r:{}]-(b) RETURN r'
	query = query.format(condStart, condEnd, rel)

	graph.cypher.execute(query)