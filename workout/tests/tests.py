from django.test import TestCase, Client

from workout.models import UserProfile, Routine, Workout

from .test_utils import *


class TestAccounts(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        self.client.post('/signup/', data={'username': 'cory@madden.com',
                                           'first_name': 'Cory',
                                           'last_name': 'Madden',
                                           'password': 'password',
                                           'password_confirm': 'password'})
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_login(self):
        create_test_user()
        response = self.client.post('/login/', data={'username': 'cory@madden.com', 'password': 'password'},
                                    follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated())


class TestRoutines(TestCase):
    def setUp(self):
        self.client = Client()
        create_test_user()

    def test_create_routine(self):
        login_test_user(self.client)
        self.client.post('/add-routine/', data={'name': 'Test Routine #1', 'day': 'TUESDAY'}, follow=True)
        self.assertEqual(Routine.objects.count(), 1)
        routine = Routine.objects.first()
        self.assertEqual(routine.name, 'Test Routine #1')
        self.assertEqual(routine.get_day_display(), 'Tuesday')

    def test_delete_routine(self):
        login_test_user(self.client)
        routine = Routine.objects.create()
        self.client.post('/delete-routine/{}/'.format(routine.id), follow=True)
        self.assertEqual(Routine.objects.count(), 0)

    def test_edit_routine(self):
        login_test_user(self.client)
        routine = Routine.objects.create()
        self.client.post('/edit-routine/{}/'.format(routine.id), data={
            'name': 'New Routine Name',
            'day': 'THURSDAY',
        }, follow=True)
        routine.refresh_from_db()
        self.assertEqual(
            {
                'name': routine.name,
                'day': routine.day,
            },
            {
                'name': 'New Routine Name',
                'day': 'THURSDAY'
            }
        )
