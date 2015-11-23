import json
from api import db

with open('lang_names.json', 'r') as f:
    names = json.load(f)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	service = db.Column(db.Enum('Facebook'))
	token = db.Column(db.String)

	def __init__(self, service, token):
		self.service = service
		self.token = token

	def __repr__(self):
		return '<User {}:{}>'.format(self.service, self.token)

class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	orig_form = db.Column(db.String)
	language = db.Column(db.String)
	definition = db.Column(db.String)
	latin_form = db.Column(db.String)
	ipa_form = db.Column(db.String)
	creator_id = db.Column(db.Integer, db.ForeignKey(User.id))

	creator = db.relationship('User', backref='created_words')

	def __init__(self, user, orig_form, language, definition=None, latin_form=None, ipa_form=None):
		self.orig_form = orig_form
		self.language = language
		self.definition = None
		self.latin_form = None
		self.ipa_form = None
		self.creator = user

	def __repr__(self):
		return '<Word {}:{}>'.format(self.language, self.orig_form)

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
		backref='roots')
	desc = db.relationship('Word', foreign_keys=[desc_id],
		backref='descs')

	creator = db.relationship('User', backref='created_rels')

	def __init__(self, user, root, desc, source):
		self.root = root
		self.desc = desc
		self.source = source
		self.creator = user

	def __repr__(self):
		return '<Rel {}->{}>'.format(self.root, self.desc)

class RelFlag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rel_id = db.Column(db.Integer, db.ForeignKey(Rel.id))
	flagger_id = db.Column(db.Integer, db.ForeignKey(User.id))

	rel = db.relationship('Rel', backref='flags')
	flagger = db.relationship('User', backref='rel_flags')

	def __init__(self, flagger, rel):
		self.rel = rel
		self.flagger = flagger

