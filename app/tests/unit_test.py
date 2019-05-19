import unittest, os
from app import app, db
from app.models import User, Poll, Recipe, Vote


class RoutesTestClass(unittest.TestCase):

    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

        u1 = User(username='user1', email='test@gmail.com')
        u1.set_password('password')
        admin1 = User(username='admin', email='admin@gmail.com', is_admin=True)
        admin1.set_password('admin')

        db.session.add(u1)
        db.session.add(admin1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # login as account
    def login(self, user, password):
        self.app.post('/login',
                      data=dict(username=user,
                                password=password,
                                ),
                      follow_redirects=True)       

    def test_register(self):
        self.app.post('/register',
                      data=dict(username='usertemp',
                                email='email@email.com',
                                password='1234',
                                password_repeat='1234'
                                ),
                      follow_redirects=True)

        # The new user is in the database
        self.assertTrue(User.query.filter_by(username='usertemp').first())

    def test_register_nametaken(self):
        response = self.app.post('/register',
                                 data=dict(username='newuser',
                                           email='test@gmail.com',
                                           password='1234',
                                           password_repeat='1234'
                                           ),
                                 follow_redirects=True)

        # The new user is in the database
        self.assertFalse(User.query.filter_by(username='newuser', email='test@gmail.com').first())

        # Email is taken
        self.assertIn(b'Please use a different email address.', response.data)

    def test_register_emailtaken(self):
        response = self.app.post('/register',
                                 data=dict(username='user1',
                                           email='email@email.com',
                                           password='1234',
                                           password_repeat='1234'
                                           ),
                                 follow_redirects=True)

        # The new user is in the database
        self.assertFalse(User.query.filter_by(username='user1', email='email@email.com').first())
        
        # Username is taken
        self.assertIn(b'Please use a different username.', response.data)

    def test_delete_user(self):
        self.login('admin', 'admin')
        self.app.post('/user/1/delete')
        self.assertFalse(User.query.filter_by(username='user1').first())

    def test_update_user(self):
        self.login('user1', 'password')
        user_id = User.query.filter_by(username='user1').first().id
        resp = self.app.post('/user/{}/update'.format(user_id),
                        data=dict(username='newuser',
                                email='newmail@g.com',
                                password='newpass',
                                password_repeat='newpass'))

        user = User.query.filter_by(id=user_id).first()
     
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass'))

    def test_add_user_admin(self):
        self.login('admin', 'admin')
        resp = self.app.post('/add_user',
                             data=dict(username='newuser5',
                                       email='email@test.com',
                                       password='newpass',
                                       is_admin=True,
                                       password_repeat='newpass'))
        
        user = User.query.filter_by(username='newuser5').first()

        self.assertEqual(user.username, 'newuser5')
        self.assertEqual(user.email, 'email@test.com')
        self.assertTrue(user.is_admin)
        self.assertTrue(user.check_password('newpass'))

    def test_add_user_not_admin(self):
        self.login('admin', 'admin')
        resp = self.app.post('/add_user',
                             data=dict(username='newuser1',
                                       email='e@test.com',
                                       password='newpass',
                                       password_repeat='newpass'),
                             follow_redirects=True)
        
        user = User.query.filter_by(username='newuser1').first()

        self.assertEqual(user.username, 'newuser1')
        self.assertEqual(user.email, 'e@test.com')
        self.assertFalse(user.is_admin)
        self.assertTrue(user.check_password('newpass'))

    def test_add_user_as_not_admin(self):
        self.login('user1', 'password')
        resp = self.app.post('/add_user',
                             data=dict(username='newuser1',
                                       email='e@test.com',
                                       password='newpass',
                                       password_repeat='newpass'),
                             follow_redirects=True)
        
        self.assertIsNone(User.query.filter_by(username='newuser1').first())

    def test_add_poll(self):
        self.login('admin', 'admin')
        self.app.post('/add_poll',
                      data=dict(name='pollname',
                                description='pdescription'))
        
        poll = Poll.query.filter_by(name='pollname')
        self.assertIsNotNone(poll)
        

    if __name__ == '__main__':
        unittest.main()


