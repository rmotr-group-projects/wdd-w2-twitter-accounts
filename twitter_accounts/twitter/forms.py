from django import forms
from django.core.exceptions import ValidationError

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
