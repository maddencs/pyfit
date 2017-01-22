import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import exceptions
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView, View

from .forms import (RegistrationForm,
                    LoginForm,
                    RoutineForm,
                    ExerciseForm,
                    ExerciseHistoryForm,
                    )
from .models import Routine, Exercise, ExerciseHistory


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


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

    def form_invalid(self, form):
        return super(LoginView, self).form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'dashboard.html'


class AddRoutineView(AjaxableResponseMixin, CreateView):
    model = Routine
    form_class = RoutineForm

    def form_valid(self, form):
        form.instance.user_id = self.request.user.user_profile.id
        return super(AddRoutineView, self).form_valid(form)


class RoutineListView(TemplateView):
    template_name = 'workout/routines/routine-list.html'

    def get_context_data(self, **kwargs):
        kwargs['routines'] = list(self.request.user.user_profile.routines.all())
        kwargs['routines'].sort()
        kwargs['add_routine_form'] = RoutineForm()
        kwargs['edit_routine_form'] = RoutineForm()
        return super(RoutineListView, self).get_context_data(**kwargs)


class RoutineDetailView(TemplateView):
    template_name = 'workout/exercises/routine-exercise-list.html'

    def get_context_data(self, **kwargs):
        kwargs['routine'] = Routine.objects.get(pk=self.kwargs['routine_id'])
        kwargs['exercises'] = list(kwargs['routine'].exercises.all())
        kwargs['exercises'].sort()
        kwargs['edit_exercise_form'] = ExerciseForm()
        kwargs['add_exercise_form'] = ExerciseForm()
        return super(RoutineDetailView, self).get_context_data(**kwargs)


class DeleteRoutineView(AjaxableResponseMixin, DeleteView):
    model = Routine
    success_url = reverse_lazy('routine_list')

    def get_object(self, queryset=None):
        return Routine.objects.get(pk=self.request.POST['routine_id'])


class EditRoutineView(AjaxableResponseMixin, UpdateView):
    form_class = RoutineForm
    model = Routine

    def get_object(self):
        return Routine.objects.get(pk=self.request.POST.get('routine_id'))


class AddExerciseView(AjaxableResponseMixin, CreateView):
    form_class = ExerciseForm
    model = Exercise
    template_name = 'workout/exercises/add-exercise.html'

    def form_valid(self, form):
        form.instance.routine_id = self.request.POST['routine_id']
        return super(AddExerciseView, self).form_valid(form)


class DeleteExerciseView(AjaxableResponseMixin, View):
    model = Exercise

    def get_success_url(self):
        return reverse_lazy('routine_detail', kwargs={'routine_id': self.routine_id})

    def get_object(self):
        exercise = Exercise.objects.get(pk=self.request.POST['exercise_id'])
        self.routine_id = exercise.routine_id
        return exercise

    def post(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            if request.is_ajax():
                return JsonResponse({
                    'success': True,
                })
            else:
                return self.get_success_url()
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'reason': 'EXERCISE_DNE',
            })


class ExerciseDetailView(TemplateView):
    template_name = 'workout/exercises/exercise-detail.html'


class EditExerciseView(AjaxableResponseMixin, UpdateView):
    form_class = ExerciseForm
    model = Exercise

    def get_object(self):
        return Exercise.objects.get(pk=self.request.POST['exercise_id'])


class AddExerciseHistoryView(AjaxableResponseMixin, CreateView):
    model = ExerciseHistory
    form_class = ExerciseHistoryForm
    template_name = 'workout/history/add-exercise-history.html'

    def form_valid(self, form):
        form.instance.exercise_id = self.kwargs['exercise_id']
        return super(AddExerciseHistoryView, self).form_valid(form)


class EditExerciseHistoryView(AjaxableResponseMixin, UpdateView):
    form_class = ExerciseHistoryForm
    model = ExerciseHistory

    def get_object(self):
        return ExerciseHistory.objects.get(pk=self.kwargs['history_id'])


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
