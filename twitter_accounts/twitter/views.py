from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout as django_logout, get_user_model
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Tweet, ValidationToken
from .forms import TweetForm, ProfileForm, RegisterForm, ChangePasswordForm, ResetPasswordForm, ConfirmResetPasswordForm

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


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    # fields = ['username', 'password', 'first_name', 'last_name', 'email', 'birth_date', 'avatar']
    template_name = 'register.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.save(commit=False)
        print(form.cleaned_data)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return HttpResponseRedirect(self.success_url)


# @method_decorator(login_required, 'dispatch')
class ChangePasswordView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ChangePasswordForm
    template_name = 'change_password.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password'])
        self.request.user.save()
        messages.success(self.request, 'Succesfully changed password!')
        return render(self.request, self.template_name)


class ResetPasswordView(FormView):
    template_name = 'reset_password.html'
    form_class = ResetPasswordForm

    def form_valid(self, form):
        if User.objects.filter(email=form.cleaned_data['email']):
            # create token
            # send email
            pass
        messages.success(self.request, 'Email sent!')
        return super().form_invalid(form)


class ConfirmChangePasswordView(FormView):
    template_name = 'confirm_reset_password.html'
    form_class = ConfirmResetPasswordForm

    def form_valid(self, form):
        token = get_object_or_404(ValidationToken, self.kwargs.get('validation_token'))
        user = User.objects.get(email=token.email)
        user.set_password(form.cleaned_data.get('new_password'))
        user.save()
        messages.success(self.request, 'Password changed!')
        token.delete()
        return super().form_valid(form)


class ValidateView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        token = get_object_or_404(ValidationToken, token=kwargs.get('validation_token'))
        user = User.objects.get(email=token.email)
        user.is_active = True
        user.email_validated = True
        user.save()
        token.delete()
        messages.success(request, 'Validation successful!')
        return redirect('/login')
