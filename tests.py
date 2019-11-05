from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Event

class DBTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='test')
        u.set_password('pass')
        self.assertFalse(u.check_password('notpass'))
        self.assertTrue(u.check_password('pass'))

    def test_follow(self):
        u = User(username='test student')
        e = Event(event_name='test event')
        db.session.add(u)
        db.session.add(e)
        db.session.commit()
        self.assertEqual(u.followed.all(), [])
        self.assertEqual(e.followers.all(), [])

        u.follow(e)
        db.session.commit()
        self.assertTrue(u.is_following(e))
        self.assertEqual(u.followed.count(), 1)
        self.assertEqual(u.followed.first().event_name, 'test event')
        self.assertEqual(e.followers.count(), 1)
        self.assertEqual(e.followers.first().username, 'test student')

        u.unfollow(e)
        db.session.commit()
        self.assertFalse(u.is_following(e))
        self.assertEqual(u.followed.count(), 0)
        self.assertEqual(e.followers.count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
