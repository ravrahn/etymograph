from flask import request, render_template
from forms import *

def request_wants_json():
    '''
    returns true if the current request has a JSON application type, false otherwise.
    This helper function from http://flask.pocoo.org/snippets/45/
    '''
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=False, **kwargs)

def render_no_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=True, **kwargs)

