from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .constants import DAYS_OF_WEEK


class RegistrationForm(forms.Form):
    username = forms.EmailField(max_length=250)
    first_name = forms.CharField(max_length=250)
    last_name = forms.CharField(max_length=250)
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'name': 'password',
                'id': 'password',
                'class': 'password',
                'placeholder': 'Password'
            }
        ),
        label='Password',
        error_messages={
            'required': 'Please enter your password.'
        }
    )
    password_confirm = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'name': 'password_confirm',
                'id': 'password_confirm',
                'class': 'password',
                'placeholder': 'Confirm Password'
            }
        ),
        label='Confirm Password',
        error_messages={
            'required': 'Please re-enter your password.'
        }
    )

    def clean(self):
        data = super(RegistrationForm, self).clean()
        if data['password'] != data['password_confirm']:
            self.add_error('password', 'Passwords do not match.')
            return
        data['email'] = data['username']

    def save(self):
        self.cleaned_data.pop('password_confirm')
        user = User.objects.create_user(**self.cleaned_data)
        return {
            'username': user.username,
            'password': self.cleaned_data.get('password'),
        }


class LoginForm(AuthenticationForm):
    username = forms.EmailField(max_length=250)
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'name': 'password',
                'id': 'password',
                'class': 'password',
                'placeholder': 'Password'
            }
        ),
        label='Password',
        error_messages={
            'required': 'Please enter your password.'
        }
    )


class BaseRoutineForm(forms.Form):
    day = forms.ChoiceField(choices=DAYS_OF_WEEK, required=False)
    name = forms.CharField(max_length=250, required=False)


class AddRoutineForm(BaseRoutineForm):
    pass


class EditRoutineForm(BaseRoutineForm):
    def save(self, routine):
        routine.update(**self.cleaned_data)
        return True

