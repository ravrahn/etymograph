from flask import request, render_template
from forms import *
from difflib import SequenceMatcher
import model

def search(query, page=None, per_page=20):
    results = model.Word.query.filter(model.Word.orig_form.like('%' + query + '%')).all()
    
    results = [word.info() for word in results]
    results = [word for word in results if word['flag_count'] < 5]

    def sort_alpha(word):
        m = SequenceMatcher(None, word['orig_form'], query)
        ratio = m.quick_ratio() + 0.0001 # cheap hack to avoid /0 errors
        return 1/ratio

    results = sorted(results, key=sort_alpha)

    length = len(results)

    if page is not None and page >= 1:
        results = results[((page-1)*per_page):(page*per_page)]

    return (results, length)

def render_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=False, **kwargs)

def render_no_search_template(*args, **kwargs):
    return render_template(*args, search_form=SearchForm(), no_form=True, **kwargs)

