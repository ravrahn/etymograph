from flask.ext.wtf import Form
from wtforms import *
from wtforms.validators import *
import re

class SearchForm(Form):
    no_spaces = re.compile(r'^\S+$', re.UNICODE)
    q = StringField('search_field', id='search_field',
            validators=[DataRequired(), Regexp(no_spaces)])

class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class RegisterForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class AddWordForm(Form):
    orig_form = StringField('Word', validators=[InputRequired()])
    lang_name = StringField('Language')
    language = StringField(validators=[InputRequired()])
    definition = TextAreaField('Definition')
    ipa_form = StringField('IPA Transcription')
    latin_form = StringField('Latin Transliteration')

class EditWordForm(Form):
    orig_form = StringField('Word', validators=[InputRequired()])
    lang_name = StringField('Language')
    language = StringField(validators=[InputRequired()])
    definition = TextAreaField('Definition')
    ipa_form = StringField('IPA Transcription')
    latin_form = StringField('Latin Transliteration')

class AddRootForm(Form):
    search = StringField('Search')
    word_id = HiddenField(validators=[InputRequired()])
    root_id = HiddenField(validators=[InputRequired()])
    source = StringField('Source')

class EditRelForm(Form):
    source = StringField('Source', validators=[InputRequired()])
