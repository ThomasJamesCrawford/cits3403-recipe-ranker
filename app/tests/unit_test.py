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
        db.session.commit()

        poll1 = Poll(name='poll1', description='pdesc', creator_id=u1.id)
        poll2 = Poll(name='poll2', description='p2desc', creator_id=u1.id)

        db.session.add(poll1)
        db.session.add(poll2)
        db.session.commit()

        recipe1 = Recipe(
            name='recipe1',
            description='rdesc',
            contributor_id=u1.id,
            poll_id=poll1.id)

        db.session.add(recipe1)
        db.session.commit()

        vote1 = Vote(
            poll_id=poll1.id,
            user_id=u1.id,
            recipe_id=recipe1.id
        )

        db.session.add(admin1)
        db.session.add(vote1)
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
        user = User.query.first()
        self.app.post('/user/{}/delete'.format(user.id))
        self.assertFalse(User.query.get(user.id))

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
        
    def test_add_poll_as_user(self):
        self.login('user1', 'password')
        self.app.post('/add_poll',
                      data=dict(name='newpoll',
                                description='pdescription'))
        
        poll = Poll.query.filter_by(name='newpoll').first()
        self.assertIsNone(poll)

    def test_add_recipe(self):
        self.login('admin', 'admin')

        poll_id = Poll.query.filter_by(name='poll1').first().id

        self.app.post('/add_recipe',
                      data=dict(name='recipename',
                                description='rdescription',
                                poll=poll_id))

        recipe = Recipe.query.filter_by(name='recipename').first()

        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.poll_id, poll_id)

    def test_add_recipe_not_admin(self):
        self.login('user1', 'password')

        poll = Poll.query.first()

        self.app.post('/add_recipe',
                      data=dict(name='recipename',
                                description='rdescription',
                                poll=poll.id))
        
        recipe = Recipe.query.filter_by(name='recipename').first()

        self.assertIsNone(recipe)

    def test_delete_vote(self):
        self.login('admin', 'admin')
        vote = Vote.query.first()

        self.app.post('/vote/{}/delete'.format(vote.id))
        
        vote = Vote.query.get(vote.id)

        self.assertIsNone(vote)

    def test_delete_vote_not_admin(self):
        self.login('user1', 'password')
        vote = Vote.query.first()

        self.app.post('/vote/{}/delete'.format(vote.id))
        
        vote = Vote.query.get(vote.id)

        self.assertIsNotNone(vote)

    def test_vote_recipe(self):
        self.login('admin', 'admin')

        recipe_id = Recipe.query.first().id
        user_id = User.query.filter_by(username='admin').first().id
        self.app.post('/recipe/{}/vote'.format(recipe_id))

        vote = Vote.query.filter_by(
            user_id=user_id, recipe_id=recipe_id).first()

        self.assertIsNotNone(vote)
        self.assertEqual(vote.recipe_id, recipe_id)
        self.assertEqual(vote.user_id, user_id)

    def test_delete_poll(self):
        self.login('admin', 'admin')

        poll_id = Poll.query.first().id
        self.app.post('/poll/{}/delete'.format(poll_id))

        poll = Poll.query.get(poll_id)
        self.assertIsNone(poll)

    def test_update_recipe(self):
        self.login('admin', 'admin')

        recipe_id = Recipe.query.first().id
        poll1_id = Recipe.query.get(recipe_id).poll_id
        poll2_id = Poll.query.filter(Poll.id != poll1_id).first().id

        self.app.post(
            '/recipe/{}/update'.format(recipe_id),
            data=dict(name='newname', description='newdesc', poll=poll2_id))

        recipe = Recipe.query.get(recipe_id)
        self.assertEqual(recipe.poll_id, poll2_id)
        self.assertEqual(recipe.name, 'newname')
        self.assertEqual(recipe.description, 'newdesc')

    def test_delete_recipe(self):
        self.login('admin', 'admin')

        recipe_id = Recipe.query.first().id
        self.app.post('/recipe/{}/delete'.format(recipe_id))

        recipe = Recipe.query.get(recipe_id)
        self.assertIsNone(recipe)

    if __name__ == '__main__':
        unittest.main()


