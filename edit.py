from flask import Blueprint, request, redirect, abort, url_for
from forms import *
from flask.ext.login import current_user, login_required


import helpers
import model

edit = Blueprint('edit', __name__)

@edit.route('/add/word', methods=['GET', 'POST'])
@login_required
def add_word():
    form = AddWordForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        word_data = form.data
        del word_data['lang_name']
        # make sure word doesn't exist
        word_check = model.Word.query.filter_by(**word_data).first()
        if word_check is None:
            # add the word to the database
            word = model.Word(current_user,
                word_data['orig_form'],
                word_data['language'],
                definition=word_data['definition'],
                latin_form=word_data['latin_form'],
                ipa_form=word_data['ipa_form'])
            model.db.session.add(word)
            model.db.session.commit()
            return redirect('/{}'.format(word.id))
        else:
            abort(400)

    langs = sorted([model.names[code] for code in model.names])
    lang_lookup = {}
    for code in model.names:
        lang_lookup[model.names[code]] = code
    return helpers.render_search_template('addword.html', form=form, langs=langs, lang_lookup=lang_lookup, title='Add Word')

@edit.route('/edit/word/<int:word_id>', methods=['GET', 'POST'])
@login_required
def edit_word(word_id):
    form = EditWordForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        word_data = form.data
        del word_data['lang_name']
        # edit the word in the database
        word = model.Word.query.get(word_id)
        word.orig_form = word_data['orig_form']
        word.language = word_data['language']
        word.definition = word_data['definition']
        word.ipa_form = word_data['ipa_form']
        word.latin_form = word_data['latin_form']
        model.db.session.commit()
        return redirect('/{}'.format(word_id))

    langs = sorted([model.names[code] for code in model.names])
    lang_lookup = {}
    for code in model.names:
        lang_lookup[model.names[code]] = code
    word = model.Word.query.get(word_id).info()
    return helpers.render_search_template('editword.html', form=form, langs=langs, lang_lookup=lang_lookup, word=word, title='Edit Word')


@edit.route('/add/root', methods=['POST'])
@login_required
def add_root():
    form = AddRootForm(request.form)
    word_id = int(form.word_id.data)
    root_id = int(form.root_id.data)
    source = form.source.data

    word = model.Word.query.get(word_id)
    root = model.Word.query.get(root_id)

    # missing words
    check = word is not None and root is not None
    if check:
        check = check and root != word
        # duplicate rel
        check = check and root not in [rel.root for rel in word.roots]
        check = check and word not in [rel.desc for rel in root.descs]
        # circular (A->B->A)
        check = check and root not in [rel.desc for rel in word.descs]
        check = check and word not in [rel.root for rel in root.roots]

    if check:
        rel = model.Rel(current_user, root, word, source)
        model.db.session.add(rel)
        model.db.session.commit()
    else:
        abort(400)
    next_url = request.args.get('next') or '/{}'.format(word_id)
    return redirect(next_url)

@edit.route('/edit/rel/<int:root_id>/<int:desc_id>', methods=['GET','POST'])
@login_required
def edit_rel(root_id, desc_id):
    form = EditRelForm(request.form)
    #get dicts of info about this relationship
    rel = model.Rel.query.filter_by(root_id=root_id, desc_id=desc_id).first()
    if rel is None:
        abort(404)
    if request.method == 'POST':
        if not form.validate():
            abort(400)
        source = form.source.data
        # edit the relationship the database 
        rel.source = source
        model.db.session.commit()
        next_url = '/{}'.format(root_id)
        return redirect(next_url)

    my_URL = url_for('edit.edit_rel', root_id=root_id, desc_id=desc_id)
    return helpers.render_search_template('edit_rel.html', form=form, root=rel.root.info(), rel=rel.info(), desc=rel.desc.info(), my_URL=my_URL, title='Edit Relation')

@edit.route('/flag/<int:word_id>', methods=['POST'])
@login_required
def flag(word_id):
    word = model.Word.query.get(word_id)

    if word is not None:
        has_flagged = False
        for flag in word.flags:
            has_flagged = (flag.flagger == current_user) or has_flagged
        if not has_flagged:
            flag = model.WordFlag(current_user, word)
            model.db.session.add(flag)
            model.db.session.commit()
        return_url = request.args.get('next')
        return redirect(return_url)
    else:
        abort(404)

@edit.route('/flag/rel/<int:root_id>/<int:desc_id>', methods=['POST'])
@login_required
def flag_rel(root_id, desc_id):
    if not root_id or not desc_id:
        abort(404) # cannot flag non-existent relations.
    rel = model.Rel.query.filter_by(root_id=root_id, desc_id=desc_id).first()

    if rel is not None:
        has_flagged = False
        for flag in rel.flags:
            has_flagged = (flag.flagger == current_user) or has_flagged
        if not has_flagged:
            flag = model.RelFlag(current_user, rel)
            model.db.session.add(flag)
            model.db.session.commit()
        return_url = request.args.get('next') or '/edit/rel/'+str(root_id)+'/'+str(desc_id)
        return redirect(return_url)
    else:
        abort(404)
