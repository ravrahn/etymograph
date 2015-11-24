from flask import Blueprint, request, redirect, abort
from forms import *

from helpers import *
from user import get_user
import model

edit = Blueprint('edit', __name__)

@edit.route('/add/word', methods=['GET', 'POST'])
def add_word():
    me = get_user()
    if me is not None:
        form = AddWordForm(request.form)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            word_data = form.data
            del word_data['lang_name']
            # make sure word doesn't exist
            word_check = model.Word.query.filter_by(**word_data).first()
            if word_check is not None:
                # add the word to the database
                word = model.Word(model.get_user(me['id']),
                    word_data['orig_form'],
                    word_data['language'],
                    definition=word_data['definition'],
                    latin_form=word_data['latin_form'],
                    ipa_form=word_data['ipa_form'])
                model.db.session.add(word)
                model.db.session.commit()
            return redirect('/{}'.format(word.id))

        langs = sorted([model.names[code] for code in model.names])
        lang_lookup = {}
        for code in model.names:
            lang_lookup[model.names[code]] = code
        return render_search_template('addword.html', form=form, langs=langs, lang_lookup=lang_lookup, title='Add Word')
    else:
        abort(403)

@edit.route('/edit/word/<int:word_id>', methods=['GET', 'POST'])
def edit_word(word_id):
    me = get_user()
    if me is not None:
        form = EditWordForm(request.form)
        if request.method == 'POST':
            if not form.validate():
                abort(400)
            word_data = form.data
            del word_data['lang_name']
            # edit the word in the database
            word = model.get_word(word_id)
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
        word = model.get_word(word_id).info()
        return render_search_template('editword.html', form=form, langs=langs, lang_lookup=lang_lookup, word=word, title='Edit Word')
    else:
        abort(403)


@edit.route('/add/root', methods=['POST'])
def add_root():
    me = get_user()
    if me is not None:
        form = AddRootForm(request.form)
        word_id = int(form.word_id.data)
        root_id = int(form.root_id.data)
        source = form.source.data

        word = model.get_word(word_id)
        root = model.get_word(root_id)

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
            rel = model.Rel(model.get_user(me['id']), root, word, source)
            model.db.session.add(rel)
            model.db.session.commit()
        else:
            abort(400)
        next_url = request.args.get('next') or '/{}'.format(word_id)
        return redirect(next_url)
    else:
        abort(403)

@edit.route('/edit/rel/<int:root_id>/<int:desc_id>', methods=['GET','POST'])
def edit_rel(root_id, desc_id):
    me = get_user()
    if me is not None:
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

        my_URL = url_for('edit_rel', root_id=root_id, desc_id=desc_id)
        return render_search_template('edit_rel.html', form=form, root=rel.root.info(), rel=rel.info(), desc=rel.desc.info(), my_URL=my_URL, title='Edit Relation')
    else:
        abort(403)

@edit.route('/flag/<int:word_id>', methods=['POST'])
def flag(word_id):
    word = model.get_word(word_id)
    me = get_user()
    if me is not None and word is not None:
        me_db = model.get_user(me['id'])
        flag = model.WordFlag(me_db, word)
        model.db.session.add(flag)
        model.db.session.commit()
        return_url = request.args.get('next')
        return redirect(return_url)
    else:
        abort(404)

@edit.route('/flag/rel/<int:root_id>/<int:desc_id>', methods=['POST'])
def flag_rel(root_id, desc_id):
    if not root_id or not desc_id:
        abort(404) # cannot flag non-existent relations.
    rel = model.Rel.query.filter_by(root_id=root_id, desc_id=desc_id).first()
    me = get_user()
    if me is not None and rel is not None:
        me_db = model.get_user(me['id'])
        flag = model.RelFlag(me_db, rel)
        model.db.session.add(flag)
        model.db.session.commit()
        return_url = request.args.get('next') or '/edit/rel/'+str(root_id)+'/'+str(desc_id)
        return redirect(return_url)
    else:
        abort(404)