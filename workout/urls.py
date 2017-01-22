from django.conf.urls import url, include
from django.contrib import admin

from workout import views as workout_views

urlpatterns = [
    url(r'^$', workout_views.DashboardView.as_view()),
    url(r'^login/$', workout_views.LoginView.as_view(), name='login'),
    url(r'^signup/$', workout_views.SignupView.as_view(), name='signup'),
    url(r'^dashboard/$', workout_views.DashboardView.as_view(), name='dashboard'),
    url(r'^add-routine/$', workout_views.AddRoutineView.as_view(), name='add_routine'),
    url(r'^routines/$', workout_views.RoutineListView.as_view(), name='routine_list'),
    url(r'^routine/(?P<routine_id>[0-9]+)/$', workout_views.RoutineDetailView.as_view(), name='routine_detail'),
    url(r'^delete-routine/$', workout_views.DeleteRoutineView.as_view(), name='delete_routine'),
    url(r'^edit-routine/$', workout_views.EditRoutineView.as_view(), name='edit_routine'),
    url(r'^add-exercise/$', workout_views.AddExerciseView.as_view(),
        name='add_exercise'),
    url(r'^delete-exercise/$', workout_views.DeleteExerciseView.as_view(), name='delete_exercise'),
    url(r'^exercise/(?P<exercise_id>[0-9]+)/$', workout_views.ExerciseDetailView.as_view(), name='exercise_detail'),
    url(r'^edit-exercise/$', workout_views.EditExerciseView.as_view(), name='edit_exercise'),
    url(r'^exercise/(?P<exercise_id>[0-9]+)/add-history/$', workout_views.AddExerciseHistoryView.as_view(),
        name='add_exercise_history'),
    url(r'^edit-exercise-history/(?P<history_id>[0-9]+)/$', workout_views.EditExerciseHistoryView.as_view(),
        name='edit_exercise_history'),
    url(r'^delete-exercise-history/(?P<history_id>[0-9]+)/$', workout_views.DeleteExerciseHistoryView.as_view(),
        name='delete_exercise_history'),
    url(r'^exercise-history-list/(?P<exercise_id>[0-9]+)/$', workout_views.ExerciseHistoryListView.as_view(),
        name='exercise_history_list'),
    url(r'^exercise-history/(?P<history_id>[0-9]+)/$', workout_views.ExerciseHistoryDetailView.as_view(),
        name='exercise_history_detail')
]
