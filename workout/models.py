import datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .constants import DAYS_OF_WEEK, USER_TYPES, EXERCISE_TYPES, EXERCISES


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)


class ModelMixin(object):
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                setattr(self, k, v)
        self.save()


class UserProfile(models.Model, ModelMixin):
    user = models.OneToOneField(User, related_name='user_profile')
    user_type = models.CharField(max_length=30, choices=USER_TYPES, default='NORMAL')

    def __str__(self):
        return '{0}, {1}'.format(self.user.last_name, self.user.first_name)

    def __unicode__(self):
        return '{0} -- {1}'.format(self.user.get_full_name(), self.user_type)

    def add_routine(self, **kwargs):
        return self.routines.create(**kwargs)


class Routine(models.Model, ModelMixin):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='routines', blank=True, null=True)
    name = models.CharField(max_length=255, default='Custom Routine')
    day = models.CharField(max_length=30, choices=DAYS_OF_WEEK, default='SUNDAY')

    def __str__(self):
        return '{0} -- {1}'.format(self.name, self.get_day_display())

    def __unicode__(self):
        return 'Routine: {0} -- ID: {1}'.format(self.name, self.id)

    def __lt__(self, other):
        self_index = DAYS_OF_WEEK.index((self.day, self.get_day_display()))
        other_index = DAYS_OF_WEEK.index((other.day, other.get_day_display()))
        return self_index < other_index

    def __eq__(self, other):
        return self.day == other.day

    def add_exercise(self, **kwargs):
        return self.exercises.create(**kwargs)


class Exercise(models.Model, ModelMixin):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='exercises', blank=True, null=True)
    priority = models.IntegerField(default=0)  # Order in which the exercise is performed
    exercise_type = models.CharField(max_length=30, choices=EXERCISE_TYPES, default='RESISTANCE')
    exercise_name = models.CharField(max_length=250, choices=EXERCISES, default='Custom Exercise')
    sets = ArrayField(models.IntegerField(default=10), size=10, default=list())
    rest_duration = models.IntegerField(default=60)  # Time represented in seconds

    def __str__(self):
        return '{0} -- {1}'.format(self.get_exercise_type_display(), self.exercise_name)

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def add_history(self, **kwargs):
        if not kwargs.get('sets', None):
            kwargs['sets'] = self.sets
        return self.history.create(**kwargs)

    def get_history_by_day(self, date=timezone.now()):
        """
        Get a list of ExerciseHistory objects for the date provided

        :param datetime.datetime date: Day of history to filter by
        :return list(ExerciseHistory):
        """
        return self.history.filter(timestamp__year=date.year, timestamp__day=date.day)

    def get_history_by_date_range(self,
                                  start_date=timezone.now() - datetime.timedelta(days=7),
                                  end_date=timezone.now()):
        start_date = start_date.replace(hour=0, minute=0)
        end_date = end_date.replace(hour=23, minute=59)
        return self.history.filter(timestamp__gte=start_date, timestamp__lte=end_date)


class ExerciseHistory(models.Model, ModelMixin):
    exercise = models.ForeignKey(Exercise, related_name='history')
    timestamp = models.DateTimeField(default=timezone.now)
    sets = ArrayField(models.IntegerField(default=10), size=10, default=list())
    weights_per_set = ArrayField(models.IntegerField(default=10), size=10, default=list())
    notes = models.TextField()

    def json(self):
        return {
            'id': self.id,
            'sets': list(map(lambda x: {
                'reps': x[0],
                'weight': x[1],
            }, tuple(zip(self.sets, self.weights_per_set))))
        }


