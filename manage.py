import sys
import math
from blessings import Terminal
from flask.ext.script import Manager  
from flask.ext.migrate import Migrate, MigrateCommand 
from model import Word, Rel, db
from app import app

REL_CONVERTER = { # (name, flip order, directional)
    'etymology': ('root', False, False),
    'etymological_origin_of': ('root', True, False),
    'etymologically_related': ('', False, False),
    'is_derived_from': ('derivation', False, False),
    'has_derived_form': ('derivation', True, False),
    'variant:orthography': ('variant', False, True)
}

manager = Manager(app)  
migrate = Migrate(app, db)  
manager.add_command('db', MigrateCommand)

@manager.command
def import_tsv(file_name):
    t = Terminal()

    with open(file_name) as importee:
        file_length = sum(1 for _ in importee)
        print('Importing {} relations'.format(file_length))

    with open(file_name) as importee:
        print('Parsing file')
        print()
        count = 0
        for line in importee:
            line = line.split('\t')

            start_data = line[0].split(':')
            start_word = None
            if '[[' not in line[0]:
                start_check = Word.query.filter_by(language=start_data[0], orig_form=start_data[1]).first()
                if start_check is None:
                    start = Word(None, start_data[1], start_data[0])
                    db.session.add(start)
                else:
                    start = start_check

            end_data = line[2].split(':')
            end = None
            if '[[' not in line[2]:
                end_check = Word.query.filter_by(language=end_data[0], orig_form=end_data[1]).first()
                if end_check is None:
                    end = Word(None, end_data[1], end_data[0])
                    db.session.add(start)
                else:
                    end = end_check


            rel_type = REL_CONVERTER[line[1][4:]]
            if rel_type[0] == 'root':
                if rel_type[1]: # flip order
                    rel = Rel(None, start, end, 'Etymological Wordnet')
                else:
                    rel = Rel(None, end, start, 'Etymological Wordnet')
                db.session.add(rel)

            count += 1
            with t.location(0):
                print(t.move_up + str(count) + ' lines added' + t.clear_eol)

    print('Committing to database')
    db.session.commit()

if __name__ == "__main__":  
    manager.run()