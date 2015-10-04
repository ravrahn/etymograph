#!/usr/local/bin/python3
"""
Coverts a file of tab-separated values into a JSON file 
describing the human-readable names of a given iso 639-3 language code
where the input is in the format
<language_code> <tab> <language name>
"""
import sys
import math
from blessings import Terminal
import json

file_name = sys.argv[1]
output_file = sys.argv[2]

t = Terminal()
word_count = 0

with open(file_name) as importee:
    file_length = sum(1 for _ in importee)

print('Importing {} names'.format(file_length))

print('Parsing input file')
print()
count = 0

# Manually add some irregular codes
names = {'p_gem': 'Proto-Germanic',
         'p_gmw': 'Proto-West-Germanic',
         'p_ine': 'Proto-Indo-European',
         'p_sla': 'Proto-Slavic',
         'gem': 'Germanic',
         'gmw': 'West-Germanic',
         'ine': 'Indo-European',
         'sla': 'Slavic',
         'nah'  : 'Nahuatl'} #TODO find meaning of "WIT" code
         
with open(file_name) as importee:
    for line in importee:
        line = line.split('\t')

        code = line[0]
        name = line[1]
        names[code] = name
        
        count += 1
        with t.location(0):
            print(t.move_up+str(count)+'/'+str( str(file_length) + t.clear_eol))
        
print('Building JSON output file')
print()

with open(output_file, "w") as exportee:
    json.dump(names, exportee, indent="  ")
    
    
    
    
    
    
    
    

