from django.conf.urls import url, include
from django.contrib import admin

from workout import views as workout_views

urlpatterns = [
    url(r'^$', workout_views.DashboardView.as_view()),
    url(r'^login/$', workout_views.LoginView.as_view(), name='login'),
    url(r'^signup/$', workout_views.SignupView.as_view(), name='signup'),
    url(r'^dashboard/$', workout_views.DashboardView.as_view(), name='dashboard'),
    url(r'^add-routine/$', workout_views.AddRoutineView.as_view(), name='add_routine'),
    url(r'^delete-routine/(?P<routine_id>[0-9]+)/$', workout_views.DeleteRoutineView.as_view(), name='delete_routine'),
    url(r'^edit-routine/(?P<routine_id>[0-9]+)/$', workout_views.EditRoutineView.as_view(), name='edit_routine'),
    url(r'^routine/(?P<routine_id>[0-9]+)/add-exercise/$', workout_views.AddExerciseView.as_view(),
        name='add_exercise'),
    url(r'^exercise/(?P<exercise_id>[0-9]+)/edit/$', workout_views.EditExerciseView.as_view(), name='edit_exercise'),
    url(r'^exercise/(?P<exercise_id>[0-9]+)/add-history/$', workout_views.AddExerciseHistoryView.as_view(),
        name='add_exercise_history'),
    url(r'^edit-exercise-history/(?P<history_id>[0-9]+)/$', workout_views.EditExerciseHistoryView.as_view(),
        name='edit_exercise_history'),
    url(r'^delete-exercise-history/(?P<history_id>[0-9]+)/$', workout_views.DeleteExerciseHistoryView.as_view(),
        name='delete_exercise_history'),
    url(r'^exercise-history/(?P<exercise_id>[0-9]+)/$', workout_views.GetExerciseHistoryView.as_view(),
        name='exercise_history'),
]
