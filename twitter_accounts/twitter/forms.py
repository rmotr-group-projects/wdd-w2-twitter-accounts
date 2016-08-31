from django import forms
from django.core.exceptions import ValidationError

from .models import Tweet, User


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content']


class RegisterForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=8)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True, widget=forms.EmailInput)
    avatar = forms.ImageField(required=False)
    birth_date = forms.DateField(required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Given username is not available')
        else:
            return username


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, min_length=8)
    new_password = forms.CharField(required=True, min_length=8)
    repeated_new_password = forms.CharField(required=True, min_length=8)

    def clean(self):
        old_password = self.cleaned_data.get("old_password")
        new_password = self.cleaned_data.get("new_password")
        repeated_new_password = self.cleaned_data.get("repeated_new_password")

        if not self.user.check_password(old_password):
            raise ValidationError("Old password is invalid.")

        if new_password != repeated_new_password:
            raise ValidationError("New passwords don't match each other.")

        if new_password == old_password:
            raise ValidationError(
                "New password can't be the same as old password.")
