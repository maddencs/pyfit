import datetime
from django.test import TestCase, Client

from workout.models import UserProfile, Routine, Exercise, ExerciseHistory

from .test_utils import *


class TestMixin(object):
    def post_ajax(self, url, data):
        return self.client.post(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def get_ajax(self, url, data):
        return self.client.get(url, data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')


class TestAccounts(TestCase, TestMixin):
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
        create_user()
        response = self.client.post('/login/', data={'username': 'cory@madden.com', 'password': 'password'},
                                    follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated())


class TestRoutines(TestCase, TestMixin):
    def setUp(self):
        self.client = Client()
        self.user = create_user()

    def test_create_routine(self):
        login_user(self.client)
        self.client.post('/add-routine/', data={'name': 'Test Routine #1', 'day': 'TUESDAY'}, follow=True)
        self.assertEqual(Routine.objects.count(), 1)
        routine = Routine.objects.first()
        self.assertEqual(routine.name, 'Test Routine #1')
        self.assertEqual(routine.get_day_display(), 'Tuesday')

    def test_routine_list(self):
        login_user(self.client)
        routine_list = [{'name': 'Pull', 'day': 'MONDAY'},
                        {'name': 'Push', 'day': 'TUESDAY'},
                        {'name': 'Legs', 'day': 'WEDNESDAY'}]
        for routine in routine_list:
            self.user.user_profile.routines.create(**routine)

        res = self.client.get('/routines/')
        self.assertEqual(len(res.context['routines']), 3)

    def test_delete_routine(self):
        login_user(self.client)
        routine = Routine.objects.create()
        self.post_ajax('/delete-routine/', {'routine_id': routine.id})
        self.assertEqual(Routine.objects.count(), 0)

    def test_edit_routine(self):
        login_user(self.client)
        routine = Routine.objects.create()
        self.client.post('/edit-routine/'.format(routine.id), data={
            'routine_id': routine.id,
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


class TestExercises(TestCase, TestMixin):
    def setUp(self):
        self.client = Client()
        create_user()

    def test_create_exercise(self):
        routine = Routine.objects.create()
        res = self.post_ajax('/add-exercise/', {
            'routine_id': routine.id,
            'sets': '5, 5, 5, 5',
            'exercise_type': 'RESISTANCE',
            'name': 'BENCH_PRESS',
            'rest_duration': 120
        })
        routine.refresh_from_db()
        self.assertEqual(routine.exercises.count(), 1)
        exercise = Exercise.objects.get(pk=res.json()['pk'])
        self.assertEqual(len(exercise.sets), 4)
        self.assertEqual(exercise.get_name_display(), 'Bench Press')

    def test_edit_exercise(self):
        exercise = Exercise.objects.create()
        res = self.post_ajax('/edit-exercise/', data={
            'exercise_id': exercise.id,
            'sets': '8, 8, 8',
            'rest_duration': 90,
        })
        exercise.refresh_from_db()
        self.assertEqual(len(exercise.sets), 3)
        self.assertEqual(exercise.name, 'Custom Exercise')

    def test_delete_exercise(self):
        exercise = Exercise.objects.create()
        res = self.post_ajax('/delete-exercise/', data={'exercise_id': exercise.id})
        self.assertEqual(Exercise.objects.count(), 0)


class TestExerciseHistory(TestCase, TestMixin):
    def setUp(self):
        self.client = Client()
        create_user()

    def test_add_exercise_history(self):
        exercise = Exercise.objects.create()
        res = self.client.post('/exercise/{}/add-history/'.format(exercise.id), data={
            'sets': '9, 10, 11',
            'weights_per_set': '180, 180, 175',
        })
        exercise.refresh_from_db()
        self.assertEqual(1, exercise.history.count())
        history = ExerciseHistory.objects.first()
        self.assertEqual([
            {
                'reps': 9,
                'weight': 180,
            },
            {
                'reps': 10,
                'weight': 180,
            },
            {
                'reps': 11,
                'weight': 175,
            },
        ],
            history.json()['sets'])

    def test_edit_exercise_history(self):
        exercise = Exercise.objects.create(sets=[20])
        history = exercise.add_history()
        self.assertEqual(history.sets, [20])
        res = self.client.post('/edit-exercise-history/{}/'.format(history.id), data={
            'sets': '20, 20, 15',
            'weights_per_set': '15, 15, 15'
        })
        history.refresh_from_db()
        self.assertEqual(history.sets, [20, 20, 15])
        self.assertEqual(history.weights_per_set, [15, 15, 15])

    def test_delete_exercise_history(self):
        exercise = Exercise.objects.create()
        history = exercise.add_history()
        res = self.client.post('/delete-exercise-history/{}/'.format(history.id))
        self.assertEqual(ExerciseHistory.objects.count(), 0)

    def test_exercise_history_methods(self):
        exercise = Exercise.objects.create()
        start_date = datetime.datetime.strptime('2017-01-01', '%Y-%m-%d')
        end_date = datetime.datetime.strptime('2017-01-15', '%Y-%m-%d')
        while start_date <= end_date:
            exercise.add_history(timestamp=start_date)
            if start_date.day % 2:  # Add an extra history on odd dates to test querying multiple histories in a day
                exercise.add_history(timestamp=start_date)

            start_date += datetime.timedelta(days=1)

        date1 = datetime.datetime.strptime('2017-01-03', '%Y-%m-%d')

        # Test getting single day's history
        self.assertEqual(exercise.get_history_by_day(date1).count(), 2)

        # Test getting date range's history
        start_date = datetime.datetime.strptime('2017-01-01', '%Y-%m-%d')
        end_date = datetime.datetime.strptime('2017-01-15', '%Y-%m-%d')
        self.assertEqual(exercise.get_history_by_date_range(start_date, end_date).count(), 23)

    def test_exercise_history_endpoints(self):
        exercise = Exercise.objects.create()
        start_date = datetime.datetime.strptime('2017-01-01', '%Y-%m-%d')
        end_date = datetime.datetime.strptime('2017-01-15', '%Y-%m-%d')
        while start_date <= end_date:
            exercise.add_history(timestamp=start_date)
            start_date += datetime.timedelta(days=1)

        res = self.get_ajax('/exercise-history-list/{}/'.format(exercise.id), {
            'start_date': '2017-01-01',
            'end_date': '2017-01-02',
        })
        self.assertEqual(2, len(res.json()['history']))

        # Test context data in template
        res = self.client.get('/exercise-history-list/{}/'.format(exercise.id), data={
            'start_date': '2017-01-01',
            'end_date': '2017-01-02',
        })
        self.assertEqual(res.context['history'].count(), 2)

        # Test history detail ajax view
        history = exercise.add_history(sets=[8, 8, 8], weights_per_set=[50, 50, 50])
        res = self.client.get('/exercise-history/{}/'.format(history.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.json()['history']['id'], history.id)

        # Test history detail template view
        res = self.client.get('/exercise-history/{}/'.format(history.id))
        self.assertEqual(res.context['history'], history)

