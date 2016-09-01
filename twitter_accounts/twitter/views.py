from braces.views import GroupRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.http.response import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout as django_logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail
from django.views.generic import FormView
from django.views.generic.base import View, TemplateView
from django.views.decorators.http import require_POST

from .models import Tweet, ValidationToken
from .forms import (TweetForm, ProfileForm, RegisterForm, ChangePasswordForm,
                    ResetPasswordForm, ConfirmResetPasswordForm)

User = get_user_model()


@login_required()
def logout(request):
    django_logout(request)
    return redirect('/')


def home(request, username=None):
    if not request.user.is_authenticated():
        if not username or request.method != 'GET':
            return redirect(settings.LOGIN_URL + '?next=%s' % request.path)

    user = request.user

    if request.method == 'POST':
        if username and username != user.username:
            return HttpResponseForbidden()
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet Created!')

    form = TweetForm()

    if username:
        user = get_object_or_404(get_user_model(), username=username)
        form = None
        tweets = Tweet.objects.filter(user=user)
    else:
        users_following = request.user.following
        tweets = Tweet.objects.filter(
            Q(user=user) | Q(user__in=users_following))

    following_profile = (request.user.is_authenticated() and
                         request.user.is_following(user))
    return render(request, 'feed.html', {
        'form': form,
        'twitter_profile': user,
        'tweets': tweets,
        'following_profile': following_profile
    })


@login_required()
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.avatar = form.cleaned_data["avatar"] or user.avatar
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.birth_date = form.cleaned_data["birth_date"]
            user.save()
            messages.success(request, 'Profile updated successfully!')
    else:
        form = ProfileForm(initial={
            "avatar": request.user.avatar,
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "birth_date": request.user.birth_date,
        })

    return render(request, 'profile.html', {
        'form': form
    })


@login_required()
@require_POST
def follow(request):
    followed = get_object_or_404(
        get_user_model(), username=request.POST['username'])
    request.user.follow(followed)
    return redirect(request.GET.get('next', '/'))


@login_required()
@require_POST
def unfollow(request):
    unfollowed = get_object_or_404(
        get_user_model(), username=request.POST['username'])
    request.user.unfollow(unfollowed)
    return redirect(request.GET.get('next', '/'))


@login_required()
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if tweet.user != request.user:
        raise PermissionDenied
    tweet.delete()
    messages.success(request, 'Tweet successfully deleted')
    return redirect(request.GET.get('next', '/'))


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = '/'

    def form_valid(self, form):
        User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["first_name"].title(),
            last_name=form.cleaned_data["last_name"].title(),
            email=form.cleaned_data["email"],
            birth_date=form.cleaned_data["birth_date"],
            avatar=form.cleaned_data["avatar"],
            is_active=False
        )
        token = ValidationToken.objects.create(
            email=form.cleaned_data["email"])
        url = 'http://twitter.com/users/validate/{}'.format(token.token)
        send_mail(
            'Validate your account.',
            'Thanks for registering. To complete the process, please click in the link below: {}'.format(url),
            'twitter@noreply.com',
            [form.cleaned_data["email"]],
            fail_silently=False,
        )
        return HttpResponseRedirect(self.get_success_url())


class ValidateUserView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        token = get_object_or_404(ValidationToken, token=kwargs.get('token'))
        user = User.objects.get(email=token.email)
        user.email_validated = True
        user.is_active = True
        user.save()
        token.delete()
        return redirect(request.GET.get('next', '/login'))


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    template_name = 'change_password.html'

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.user = self.request.user
        return form

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data["new_password"])
        self.request.user.save()
        messages.success(self.request, 'Password changed successfully!')
        return render(self.request, self.template_name)


class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    template_name = 'reset_password.html'

    def form_valid(self, form):
        if User.objects.filter(email=form.cleaned_data.get('email')).exists():
            token = ValidationToken.objects.create(
                email=form.cleaned_data.get('email'))
            url = 'http://twitter.com/users/confirm-reset-password/{}'.format(token.token)
            send_mail(
                'Password recovery.',
                'To reset your password, please click in the link below: {}'.format(url),
                'twitter@noreply.com',
                [form.cleaned_data.get('email')],
                fail_silently=False,
            )
        messages.success(self.request, 'Email sent!')
        return render(self.request, self.template_name)


class ConfirmResetPasswordView(FormView):
    form_class = ConfirmResetPasswordForm
    template_name = 'confirm_reset_password.html'

    def form_valid(self, form):
        token = get_object_or_404(ValidationToken, token=self.kwargs.get('token'))
        user = User.objects.get(email=token.email)
        user.set_password(form.cleaned_data['new_password'])
        user.save()
        token.delete()
        return redirect(self.request.GET.get('next', '/'))


class DashboardView(GroupRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = 'dashboard.html'
    group_required = "Admin users"

    def no_permissions_fail(self, request=None):
        return HttpResponseForbidden()
