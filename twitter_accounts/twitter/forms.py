from django import forms
from django.core.exceptions import ValidationError
from django.core import validators

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
        fields = ('first_name', 'last_name', 'email', 'avatar', 'birth_date')


class RegisterForm(forms.ModelForm):
    first_name = OnlyLettersField(required=True)
    last_name = OnlyLettersField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'birth_date', 'avatar']


class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    new_password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    repeated_new_password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the user_id as an attribute of the form
        self.user = user

    def clean(self):
        old_password = self.cleaned_data['old_password']
        new_password = self.cleaned_data['new_password']
        repeated_new_password = self.cleaned_data['repeated_new_password']

        if not self.user.check_password(old_password):
            raise ValidationError('Old password is incorrect')

        if new_password != repeated_new_password:
            raise ValidationError('The new passwords don\'t match')

    class Meta:
        model = User
        fields = []
