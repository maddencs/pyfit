from django.test import TestCase, Client

from workout.models import UserProfile, Routine, Exercise

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


class TestExercises(TestCase):
    def setUp(self):
        self.client = Client()
        create_test_user()

    def test_create_exercise(self):
        routine = Routine.objects.create()
        res = self.client.post('/routine/{}/add-exercise/'.format(routine.id), data={
            'sets': '5, 5, 5, 5',
            'exercise_type': 'RESISTANCE',
            'exercise_name': 'BENCH_PRESS',
            'rest_duration': 120
        })
        routine.refresh_from_db()
        self.assertEqual(routine.exercises.count(), 1)
        exercise = Exercise.objects.get(pk=res.json()['exercise_id'])
        self.assertEqual(len(exercise.sets), 4)
        self.assertEqual(exercise.get_exercise_name_display(), 'Bench Press')

    def test_edit_exercise(self):
        exercise = Exercise.objects.create()
        res = self.client.post('/exercise/{}/edit/'.format(exercise.id), data={
            'sets': '8, 8, 8',
            'rest_duration': 90,
        }, follow=True)
        exercise.refresh_from_db()
        self.assertEqual(len(exercise.sets), 3)
        self.assertEqual(exercise.exercise_name, 'Custom Exercise')
