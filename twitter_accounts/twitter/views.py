from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout as django_logout, get_user_model
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Tweet
from .forms import TweetForm, ProfileForm, RegisterForm

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


class Register(CreateView):
    model = User
    form_class = RegisterForm
    # fields = ['username', 'password', 'first_name', 'last_name', 'email', 'birth_date', 'avatar']
    template_name = 'register.html'
    success_url = '/'



def change_password(request):
    pass


def reset_password(request):
    pass


def confirm_change_password(request, validation_token):
    pass


def validate(request, validation_token):
    pass
