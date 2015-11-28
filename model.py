import json
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

with open('lang_names.json', 'r') as f:
    names = json.load(f)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, name):
        self.username = username
        self.password = generate_password_hash(password)
        self.name = name

    def __repr__(self):
        return '<User {}:{}>'.format(self.username, self.authenticated)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return self.authenticated
    def is_anonymous(self):
        return False
    def is_active(self):
        return True
    def get_id(self):
        return str(self.id)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orig_form = db.Column(db.String)
    language = db.Column(db.String)
    definition = db.Column(db.String)
    latin_form = db.Column(db.String)
    ipa_form = db.Column(db.String)
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id))

    creator = db.relationship('User', backref='created_words')

    def __init__(self, user, orig_form, language, 
        definition=None, latin_form=None, ipa_form=None):
        self.orig_form = orig_form
        self.language = language
        self.definition = definition
        self.latin_form = latin_form
        self.ipa_form = ipa_form
        self.creator = user

    def __repr__(self):
        return '<Word {}:{}>'.format(self.language, self.orig_form)

    def info(self):
        info = {}
        info['id'] = self.id
        info['orig_form'] = self.orig_form
        info['language'] = self.language
        info['lang_name'] = names[self.language]
        if self.definition is not None:
            info['definition'] = self.definition
        if self.latin_form is not None:
            info['latin_form'] = self.latin_form
        if self.ipa_form is not None:
            info['ipa_form'] = self.ipa_form
        info['flag_count'] = len(self.flags)
        return info

    def get_roots(self, depth=None):
        if depth == 0:
            return self.info()
        elif depth is not None:
            depth -= 1
        roots = []
        for rel in self.roots:
            roots.append(rel.root.get_roots(depth=depth))
        info = self.info()
        info['roots'] = roots
        return info

    def get_descs(self, depth=None):
        if depth == 0:
            return self.info()
        elif depth is not None:
            depth -= 1
        descs = []
        for rel in self.descs:
            descs.append(rel.desc.get_descs(depth=depth))
        info = self.info()
        info['descs'] = descs
        return info

class WordFlag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey(Word.id))
    flagger_id = db.Column(db.Integer, db.ForeignKey(User.id))

    word = db.relationship('Word', backref='flags')
    flagger = db.relationship('User', backref='word_flags')

    def __init__(self, flagger, word):
        self.word = word
        self.flagger = flagger


class Rel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    root_id = db.Column(db.Integer, db.ForeignKey(Word.id))
    desc_id = db.Column(db.Integer, db.ForeignKey(Word.id))
    source = db.Column(db.String)
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id))  

    root = db.relationship('Word', foreign_keys=[root_id],
        backref='descs')
    desc = db.relationship('Word', foreign_keys=[desc_id],
        backref='roots')

    creator = db.relationship('User', backref='created_rels')

    def __init__(self, user, root, desc, source):
        self.root = root
        self.desc = desc
        self.source = source
        self.creator = user

    def __repr__(self):
        return '<Rel {}->{}>'.format(self.root, self.desc)

    def info(self):
        info = {}
        info['root'] = self.root.info()
        info['desc'] = self.desc.info()
        info['source'] = self.source
        info['flag_count'] = len(self.flags)
        return info


class RelFlag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rel_id = db.Column(db.Integer, db.ForeignKey(Rel.id))
    flagger_id = db.Column(db.Integer, db.ForeignKey(User.id))

    rel = db.relationship('Rel', backref='flags')
    flagger = db.relationship('User', backref='rel_flags')

    def __init__(self, flagger, rel):
        self.rel = rel
        self.flagger = flagger
