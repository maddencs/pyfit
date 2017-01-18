from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User)
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

    def add_exercise(self, **kwargs):
        return self.exercises.create(**kwargs)


class Exercise(models.Model, ModelMixin):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='exercises', blank=True, null=True)
    exercise_type = models.CharField(max_length=30, choices=EXERCISE_TYPES, default='RESISTANCE')
    exercise_name = models.CharField(max_length=250, choices=EXERCISES, default='Custom Exercise')
    sets = ArrayField(models.IntegerField(default=10), size=10, default=list())
    rest_duration = models.IntegerField(default=60)  # Time represented in seconds

    def __str__(self):
        return '{0} -- {1}'.format(self.get_exercise_type_display(), self.exercise_name)
