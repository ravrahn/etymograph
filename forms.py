from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import *
import re

class SearchForm(Form):
    # I don't know enough about Python3's unicode and regex to tell if the below will work
    # Get the field but validate against any white space
    no_spaces = re.compile(r'^\S+$', re.UNICODE)
    q = StringField('search_field', id='search_field',
            validators=[DataRequired(), Regexp(no_spaces)])

""" For later
class LoginForm(Form): # For later
   username = StringField('name', validators[DataRequired()])
   password = StringField('password', validators[DataRequired()])
   remember_me = BooleanField('remember_me', default=False)
"""


class AddWordForm(Form):
    orig_form = StringField('Word', validators=[InputRequired()])
    lang_name = StringField('Language')
    language = StringField(validators=[InputRequired()])
    definition = TextAreaField('Definition')
    ipa_form = StringField('IPA Transcription')
    eng_form = StringField('Latin Transliteration')

class AddRootForm(Form):
    word_id = IntegerField(label='Desc ID')
    root_id = IntegerField(label='Root ID')
    source = StringField('Source')

class EditRelForm(Form):
    source = StringField('Source', validators=[InputRequired()])
