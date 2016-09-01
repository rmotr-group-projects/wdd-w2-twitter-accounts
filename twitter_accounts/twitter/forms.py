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

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name',
                  'email', 'avatar', 'birth_date')

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


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(required=True)


class ConfirmResetPasswordForm(forms.Form):
    new_password = forms.CharField(required=True, min_length=8)
    repeated_new_password = forms.CharField(required=True, min_length=8)

    def clean(self):
        new_password = self.cleaned_data.get("new_password")
        repeated_new_password = self.cleaned_data.get("repeated_new_password")

        if new_password != repeated_new_password:
            raise ValidationError("New passwords don't match each other.")
