"""
Unit test module
The setUp() and tearDown() methods are special methods that the unit testing framework
executes before and after each test respectively. The application configuration is
cahnged to sqlite:// to use an in-memory SQLite database during the tests instead
the original one.
Run test by: python tests.py
"""
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
from config import Config

class TestConfig(Config):
    """define own test configuration for running tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    """test user model"""
    def setUp(self):
        """set-up the by using separate test config"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        # Flask pushes an application context, i.e bringing current_app and g to life.
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """ end session and drop all data"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """test passwoord handling"""
        user = User(username='henry')
        user.set_password('cat')
        self.assertFalse(user.check_password('dog'))
        self.assertTrue(user.check_password('cat'))

    def test_avatar(self):
        """test avatar"""
        user = User(username='mauermbq', email='mark@mauerwerk.biz')
        self.assertEqual(user.avatar(128),
                         ('https://www.gravatar.com/avatar/'
                          '902f85c5068b5726f83f053b126b9514'
                          '?d=identicon&s=128'))

    def test_follow(self):
        """add some users and test especially folllowers function"""
        u_1 = User(username='mark', email='mark@mauerwerk.biz')
        u_2 = User(username='henry', email='henry@example.com')
        db.session.add(u_1)
        db.session.add(u_2)
        db.session.commit()
        self.assertEqual(u_1.followed.all(), [])
        self.assertEqual(u_1.followers.all(), [])

        u_1.follow(u_2)
        db.session.commit()
        self.assertTrue(u_1.is_following(u_2))
        self.assertEqual(u_1.followed.count(), 1)
        self.assertEqual(u_1.followed.first().username, 'henry')
        self.assertEqual(u_2.followers.count(), 1)
        self.assertEqual(u_2.followers.first().username, 'mark')

        u_1.unfollow(u_2)
        db.session.commit()
        self.assertFalse(u_1.is_following(u_2))
        self.assertEqual(u_1.followed.count(), 0)
        self.assertEqual(u_2.followers.count(), 0)

    def test_follow_posts(self):
        """test the follower function"""
        # create four users
        u_1 = User(username='mark', email='mark@mauerwerk.biz')
        u_2 = User(username='henry', email='henry@example.com')
        u_3 = User(username='mary', email='mary@example.com')
        u_4 = User(username='david', email='david@example.com')
        db.session.add_all([u_1, u_2, u_3, u_4])

        # create four posts
        now = datetime.utcnow()
        p_1 = Post(body="post from mark", author=u_1,
                   timestamp=now + timedelta(seconds=1))
        p_2 = Post(body="post from henry", author=u_2,
                   timestamp=now + timedelta(seconds=4))
        p_3 = Post(body="post from mary", author=u_3,
                   timestamp=now + timedelta(seconds=3))
        p_4 = Post(body="post from david", author=u_4,
                   timestamp=now + timedelta(seconds=2))
        db.session.add_all([p_1, p_2, p_3, p_4])
        db.session.commit()

        # setup the followers
        u_1.follow(u_2)  # mark follows henry
        u_1.follow(u_4)  # mark follows david
        u_2.follow(u_3)  # henry follows mary
        u_3.follow(u_4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f_1 = u_1.followed_posts().all()
        f_2 = u_2.followed_posts().all()
        f_3 = u_3.followed_posts().all()
        f_4 = u_4.followed_posts().all()
        self.assertEqual(f_1, [p_2, p_4, p_1])
        self.assertEqual(f_2, [p_2, p_3])
        self.assertEqual(f_3, [p_3, p_4])
        self.assertEqual(f_4, [p_4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
