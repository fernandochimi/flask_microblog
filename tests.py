# coding: utf-8
#!flask/bin/python
import os
import unittest


from datetime import datetime, timedelta
from config import basedir
from app import app, db
from app.models import User, Post
from app.translate import microsoft_translate
from coverage import coverage
cov = coverage(branch=True, omit=['flask/*', 'tests.py'])
cov.start()


class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_avatar(self):
		u=User(nickname='fernando', email='fernando@chimi.com')
		avatar=u.avatar(128)
		expected='http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
		assert avatar[0:len(expected)] == expected

	def test_make_unique_nickname(self):
		u=User(nickname='fernando', email='fernando@chimi.com')
		db.session.add(u)
		db.session.commit()
		nickname = User.make_unique_nickname('outro')
		assert nickname == 'outro'
		nickname = User.make_unique_nickname('fernando')
		assert nickname != 'fernando'
		u=User(nickname=nickname, email='outro@chimi.com')
		db.session.add(u)
		db.session.commit()
		nickname2=User.make_unique_nickname('fernando')
		assert nickname2 != 'fernando'
		assert nickname2 != nickname

	def test_follow(self):
		u1=User(nickname='fernando', email='fernando@chimi.com')
		u2=User(nickname='matheus', email='matheus@oliveira.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		assert u1.unfollow(u2) == None
		u=u1.follow(u2)
		db.session.add(u)
		db.session.commit()
		assert u1.follow(u2) == None
		assert u1.is_following(u2)
		assert u1.followed.count() == 1
		assert u1.followed.first().nickname == 'matheus'
		assert u2.followers.count() == 1
		assert u2.followers.first().nickname == 'fernando'
		u=u1.unfollow(u2)
		assert u != None
		db.session.add(u)
		db.session.commit()
		assert u1.is_following(u2) == False
		assert u1.followed.count() == 0
		assert u2.followers.count() == 0

	def test_follow_posts(self):
		u1=User(nickname='fernando', email='fernando@chimi.com')
		db.session.add(u1)

		utcnow=datetime.utcnow()
		p1=Post(body='post from fernando', author=u1, timestamp=utcnow+timedelta(seconds=1))
		db.session.add(p1)
		db.session.commit()

		u1.follow(u1)
		db.session.add(u1)
		db.session.commit()

		f1=u1.followed_posts().all()
		assert len(f1) == 3
		assert f1 == [p4, p2, p1]

	def test_translation(self):
		assert microsoft_translate(u'English', 'en', 'es') == u'Inglés'
		assert microsoft_translate(u'Español', 'es', 'en') == u'Spanish'

	def test_delete_post(self):
		u = User(nickname='fernando', email='fernando@chimi.com')
		p = Post(body='test-point', author=u, timestamp=datetime.utcnow())
		db.session.add(u)
		db.session.add(p)
		db.session.commit()
		p = Post.query.get(1)
		db.session.remove()
		db.session.db.create_scoped_session()
		db.session.delete(p)
		db.session.commit()

	def test_user(self):
		n = User.make_valid_nickname('fernandochimi')
		assert n == 'fernandochimi'
		n = User.make_valid_nickname('fernando_chimi')
		assert n == 'fernandochimi'
		u = User(nickname='fernandochimi', email='fernando@chimi.com')
		db.session.add(u)
		db.session.commit()
		assert u.is_authenticated() == True
		assert u.is_active() == True
		assert u.is_anonymous() == False
		assert u.id == int(u.get_id())

if __name__ == '__main__':
	try:
		unittest.main()
	except:
		pass
	cov.stop()
	cov.save()
	print "\n\nCoverage report:\n"
	cov.report()
	print "HTML Version: " + os.path.join(basedir, "tmp/coverage/index.html")
	cov.html_report(directory = 'tmp/coverage')
	cov.erase()