from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Regexp
import re

class SearchForm(Form):
    # I don't know enough about Python3's unicode and regex to tell if the below will work
    # Get the field but validate against any white space
    no_spaces = re.compile(r'^\S+$', re.UNICODE)
    query = StringField('search_field', id='search_field',
            validators=[DataRequired(), Regexp(no_spaces)])

""" For later
class LoginForm(Form): # For later
   username = StringField('name', validators[DataRequired()])
   password = StringField('password', validators[DataRequired()])
   remember_me = BooleanField('remember_me', default=False)
"""
