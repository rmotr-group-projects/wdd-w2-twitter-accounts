from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Tweet, User


class OnlyLettersField(forms.CharField):

    def clean(self, value):
        if not value.isalpha():
            raise ValidationError('This field must contain only letters.')
        else:
            return value


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content']


class ProfileForm(forms.ModelForm):
    first_name = OnlyLettersField(required=False)
    last_name = OnlyLettersField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'birth_date', 'avatar')
        
class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        # ('username','password', 'first_name', 'last_name', 'email', 'birth_date', 'avatar')
        fields = ('username','password') + ProfileForm.Meta.fields
        labels = {
            'username': _('Username (*)'), 'password': _('Password (*)'), 'first_name': _('First name (*)'),
            'last_name': _('Last name (*)'), 'email': _('Email (*)'), 'birth_date': _('Birth date'),
            'avatar': _('Profile Image')
            }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': "Your username", "class": "form-control"}),
            'password': forms.PasswordInput(attrs={'placeholder': "Your password (at least 8 characters)", "class": "form-control"}),
            'first_name': forms.TextInput(attrs={'placeholder': "Your first name", "class": "form-control"}),
            'last_name': forms.TextInput(attrs={'placeholder': "Your last name", "class": "form-control"}),
            'email': forms.TextInput(attrs={'placeholder': "Your email", "class": "form-control"}),
            'birth_date': forms.DateInput(attrs={'placeholder': 'Your birth date (i.e: 1990-12-31)', "class": "form-control"}),
            
        }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'label': "Old password(*)", 'placeholder': "Your old password", "class": "form-control"}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'label': "New password(*)", 'placeholder': "Your new password", "class": "form-control"}))
    repeated_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'label': "Repeated new password(*)", 'placeholder': "Your repeated new password", "class": "form-control"}))

# class ChangePasswordForm(forms.Form):
#     class Meta:
#         model = User
#         fields = ('password',)
#         labels = {
#             'password': _('Old password (*)'), 'new_password': _('New password (*)'),
#             'new_repeat_password': _('Repeated new password (*)'),
#             }
#         widgets = {
#             'password': forms.PasswordInput(attrs={'placeholder': "Your password (at least 8 characters)", "class": "form-control"}),
#         }
