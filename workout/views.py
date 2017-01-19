from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import exceptions
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
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

    def form_valid(self, form):
        try:
            routine = Routine.objects.get(pk=self.kwargs['routine_id'])
            exercise = routine.add_exercise(**form.cleaned_data)
            return JsonResponse({
                'success': True,
                'exercise_id': exercise.id,
            })
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

    def form_valid(self, form):
        exercise = Exercise.objects.get(pk=self.kwargs['exercise_id'])
        history = exercise.add_history(**form.cleaned_data)
        return JsonResponse({
            'success': True,
            'history_id': history.id,
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'reason': form.errors,
        })


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

