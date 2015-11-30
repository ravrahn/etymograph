from flask import request, render_template
from forms import *
from difflib import SequenceMatcher
import model

def search(query):
    results = model.Word.query.filter(model.Word.orig_form.like('%' + query + '%')).all()
    
    results = [word.info() for word in results]

    def sort_alpha(word):
        m = SequenceMatcher(None, word['orig_form'], query)
        ratio = m.quick_ratio() + 0.0001 # cheap hack to avoid /0 errors
        return 1/ratio

    results = sorted(results, key=sort_alpha)

    return results

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=False, **kwargs)

def render_no_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=True, **kwargs)

