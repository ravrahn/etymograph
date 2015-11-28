from flask.ext.testing import TestCase
from model import *
from app import db, app

TEST_SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

class MyTest(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLALCHEMY_DATABASE_URI
        return app

    def setUp(self):
        db.create_all()
        # create user
        user = User('test', 'pass', 'John Doe')
        db.session.add(user)
        # create words
        word = Word(user, 'doot', 'en')
        word2 = Word(user, 'calcio', 'it')
        rel = Rel(user, word, word2, 'brain')
        db.session.add(word)
        db.session.add(word2)
        db.session.add(rel)
        # commit
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_creator(self):
        word = Word.query.filter_by(orig_form='doot').first()
        rel = Rel.query.all()[0]
        assert word.creator.username == 'test'
        assert rel.creator.username == 'test'

    def test_rel(self):
        user = User.query.all()[0]
        words = Word.query.all()
        word = words[0]
        word2 = words[1]
        rel = Rel.query.all()[0]
        assert rel.root == word
        assert rel in word.descs
        assert rel.desc == word2
        assert rel in word2.roots

    def test_flags(self):
        user = User.query.all()[0]
        word = Word.query.all()[0]
        rel = Rel.query.all()[0]
        word_flag = WordFlag(user, word)
        rel_flag = RelFlag(user, rel)
        db.session.add(word_flag)
        db.session.add(rel_flag)
        assert len(word.flags) == 1
        assert len(rel.flags) == 1

    def test_users(self):
        user = User.query.all()[0]
        user_id = user.get_id()
        assert user == User.query.get(int(user_id))
        assert not user.is_anonymous()
        assert user.is_active()

    def test_get_all_words(self):  
        words = Word.query.all()
        assert len(words) == 2, 'Expect all words to be returned'

    def test_get_word(self):  
        word = Word.query.filter_by(orig_form='doot').first()
        assert word.language == 'en', 'Expect the correct word to be returned'