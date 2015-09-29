#!/usr/local/bin/python3
import sys
import math
from blessings import Terminal
from py2neo import *

from word import *

REL_CONVERTER = { # (name, flip order, directional)
    'etymology': ('root', False, False),
    'etymological_origin_of': ('root', True, False),
    'etymologically_related': False,
    'is_derived_from': ('derivation', False, False),
    'has_derived_form': ('derivation', True, False),
    'variant:orthography': ('variant', False, True)
}

LINE_CAP = 2000
iterations = 0

file_name = sys.argv[1]

t = Terminal()
graph = Graph('http://etymograph.com:7474/db/data')
word_count = 0

with open(file_name) as importee:
    file_length = sum(1 for _ in importee)

print('Importing {} relations in {} iterations'.format(file_length, math.ceil(file_length/LINE_CAP)))

while file_length > LINE_CAP * iterations:
    words = {}
    rels = []

    graph_rels = []
    graph_nodes = {}

    if iterations > 0:
        print((t.clear_eol + t.move_up) * 6)
    print('Iteration ' + str(iterations+1))
    print('Parsing file')
    print()
    count = 0
    with open(file_name) as importee:
        for i in range((iterations*LINE_CAP)-1):
            next(importee)
        for line in importee:
            line = line.split('\t')

            start = line[0].split(':')
            if line[0] not in words and '[[' not in line[0]:
                start_word = Word(start[1], start[0])
                start_word.get_node(graph)
                words[line[0]] = start_word

            end = line[2].split(':')
            if line[2] not in words and '[[' not in line[2]:
                end_word = Word(end[1], end[0])
                end_word.get_node(graph)
                words[line[2]] = end_word

            rel_type = REL_CONVERTER[line[1][4:]]
            if rel_type:
                if rel_type[1]: # flip order
                    rel = (line[2], rel_type[0], line[0], rel_type[2])
                else:
                    rel = (line[0], rel_type[0], line[2], rel_type[2])
                if rel not in rels and '[[' not in line[0] and '[[' not in line[2]:
                    rels.append(rel)

            count += 1
            with t.location(0):
                print(t.move_up + str(count) + '/' + str(min(1+file_length-(LINE_CAP*iterations), LINE_CAP)) + t.clear_eol)
            if count >= LINE_CAP:
                break

    print('Creating relations')
    print()
    count = 0
    for rel in rels:
        start = words[rel[0]]
        end = words[rel[2]]

        graph_rel = Relationship(start.get_node(graph), rel[1], end.get_node(graph))

        add_rel = graph_rel not in graph_rels

        if not rel[3] and add_rel: # if direction is arbitrary, check both ways
            temp_rel = Relationship(end.get_node(graph), rel[1], end.get_node(graph))
            add_rel = temp_rel not in graph_rels

        if add_rel:
            graph_rels.append(graph_rel)
            add_relationship(graph, start, end, rel[1])

        count += 1
        with t.location(0):
            print(t.move_up + str(count) + '/' + str(len(rels)) + t.clear_eol)


    iterations += 1


