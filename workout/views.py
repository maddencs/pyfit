import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import exceptions
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, View

from .forms import (RegistrationForm,
                    LoginForm,
                    RoutineForm,
                    ExerciseForm,
                    ExerciseHistoryForm,
                    )
from .models import Routine, Exercise, ExerciseHistory


class SignupView(FormView):
    template_name = 'accounts/signup.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user_data = form.save()
        user = authenticate(username=user_data['username'], password=user_data['password'])
        login(self.request, user)
        return super(SignupView, self).form_valid(form)


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(self.request, user)
        return super(LoginView, self).form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'dashboard.html'


class AddRoutineView(FormView):
    form_class = RoutineForm

    def form_valid(self, form):
        routine = self.request.user.userprofile.add_routine(**form.cleaned_data)
        return JsonResponse({
            'success': True,
            'routine_id': routine.id,
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        })


class RoutineDetailView(TemplateView):
    template_name = 'workout/routine-detail.html'

    def get_context_data(self, **kwargs):
        kwargs['routine'] = Routine.objects.get(pk=self.kwargs['routine_id'])
        return super(RoutineDetailView, self).get_context_data(**kwargs)


class DeleteRoutineView(View):
    def post(self, request, *args, **kwargs):
        try:
            Routine.objects.get(pk=kwargs['routine_id']).delete()
            return JsonResponse({
                'success': True,
            })
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'reason': 'ROUTINE_DNE'  # Routine matching primary key does not exist
            })


class EditRoutineView(FormView):
    form_class = RoutineForm

    def form_valid(self, form):
        try:
            routine = Routine.objects.get(pk=self.kwargs['routine_id'])
            form.update(routine)
            return JsonResponse({
                'success': True
            })
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'reason': 'ROUTINE_DNE'  # Routine matching primary key does not exist
            })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'reason': form.errors,
        })


class AddExerciseView(FormView):
    form_class = ExerciseForm
    template_name = 'workout/add-exercise.html'

    def get_success_url(self):
        return reverse_lazy('exercise_detail', kwargs={'exercise_id': self.kwargs['exercise'].id})

    def get_context_data(self, **kwargs):
        kwargs['routine'] = Routine.objects.get(pk=self.kwargs['routine_id'])
        return super(AddExerciseView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            exercise = Routine.objects.get(pk=self.kwargs['routine_id']).add_exercise(**form.cleaned_data)
            if self.request.is_ajax():
                return JsonResponse({
                    'success': True,
                    'exercise_id': exercise.id,
                })
            else:
                self.kwargs['exercise'] = exercise
                return super(AddExerciseView, self).form_valid(form)
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'reason': 'ROUTINE_DNE'
            })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'reason': form.errors,
        })


class ExerciseDetailView(TemplateView):
    template_name = 'workout/exercise-detail.html'


class EditExerciseView(FormView):
    form_class = ExerciseForm

    def form_valid(self, form):
        exercise = Exercise.objects.get(pk=self.kwargs['exercise_id'])
        form.update(exercise)
        return JsonResponse({
            'success': True,
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'reason': form.errors,
        })


class AddExerciseHistoryView(FormView):
    form_class = ExerciseHistoryForm
    template_name = 'workout/history/add-exercise-history.html'

    def get_success_url(self):
        return reverse_lazy('exercise_history_detail', kwargs={'history_id': self.kwargs['history'].id})

    def form_valid(self, form):
        exercise = Exercise.objects.get(pk=self.kwargs['exercise_id'])
        history = exercise.add_history(**form.cleaned_data)
        if self.request.is_ajax():
            return JsonResponse({
                'success': True,
                'history_id': history.id,
            })
        else:
            self.kwargs['history'] = history
            return super(AddExerciseHistoryView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({
                'success': False,
                'reason': form.errors,
            })
        else:
            return super(AddExerciseHistoryView, self).form_invalid(form)


class EditExerciseHistoryView(FormView):
    form_class = ExerciseHistoryForm

    def form_valid(self, form):
        history = ExerciseHistory.objects.get(pk=self.kwargs['history_id'])
        form.update(history)
        return JsonResponse({
            'success': True,
            'history_id': history.id,
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'reason': form.errors,
        })


class DeleteExerciseHistoryView(View):
    def post(self, request, *args, **kwargs):
        try:
            ExerciseHistory.objects.get(pk=kwargs['history_id']).delete()
            return JsonResponse({
                'success': True,
            })
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'reason': 'HISTORY_DNE'  # History matching primary key does not exist
            })


class ExerciseHistoryListView(TemplateView):
    template_name = 'workout/history/exercise-history-report-base.html'

    def dispatch(self, request, *args, **kwargs):
        exercise = Exercise.objects.get(pk=kwargs['exercise_id'])
        if request.is_ajax():
            history = self.get_history(exercise, request.GET, kwargs)
            history = [x.json() for x in history]
            return JsonResponse({
                'success': True,
                'history': history,
            })
        return super(ExerciseHistoryListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        exercise = Exercise.objects.get(pk=kwargs['exercise_id'])
        kwargs['history'] = self.get_history(exercise, self.request.GET, kwargs).all()
        return super(ExerciseHistoryListView, self).get_context_data(**kwargs)

    @staticmethod
    def get_history(exercise, data, kwargs):
        report_type = data.get('report_type', 'date_range')
        if report_type == 'date_range':
            kwargs['date_range_history'] = True
            start_date_str = data.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
            end_date_str = data.get('end_date', timezone.now().strftime('%Y-%m-%d'))
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            history = exercise.get_history_by_date_range(start_date, end_date)
        else:
            kwargs['date_range_history'] = False
            date = datetime.datetime.strptime(data.get('date'), '%Y-%m-%d')
            history = exercise.get_history_by_day(date)
        return history


class ExerciseHistoryDetailView(TemplateView):
    template_name = 'workout/history/exercise-history-detail.html'

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            history = ExerciseHistory.objects.get(pk=kwargs['history_id'])
            return JsonResponse({
                'success': True,
                'history': history.json(),
            })
        return super(ExerciseHistoryDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['history'] = ExerciseHistory.objects.get(pk=kwargs['history_id'])
        return super(ExerciseHistoryDetailView, self).get_context_data(**kwargs)

