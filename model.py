from py2neo import *
from word import *

graph = Graph('http://etymograph.com:7474/db/data')

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
	return {}

def search(query):
	'''
	This function should return an array of search results given
	a string to search for.
	'''
	return []