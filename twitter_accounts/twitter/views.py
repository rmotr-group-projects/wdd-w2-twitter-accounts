from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout as django_logout, get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_POST

from django.views.generic import FormView, RedirectView, TemplateView
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .models import Tweet, ValidationToken
from .forms import TweetForm, ProfileForm, RegisterForm, ChangePasswordForm

#============ Pre-coded ========================================================

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
    
#============ Pre-coded ========================================================

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    
    
    def form_valid(self, form):
        type_token = 'v'
        validate_email_token = get_random_string(length=16)
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            birth_date=form.cleaned_data['birth_date'],
            avatar=form.cleaned_data['avatar'],
            is_active=False,
            )
        user.save()
        
        validation_token = ValidationToken.objects.create(user = User.objects.get(username=form.cleaned_data['username']), 
                            email=form.cleaned_data['email'],token_type=type_token, token=validate_email_token)
        validation_token.save()
        send_mail("Validation email for Twitter",
                "Thanks for registering. To complete the process, "
                "please click in the link below: "
                "http://twitter.com/users/validate/{}".format(validate_email_token),
                'admin@twitter_accounts.com',
                [form.cleaned_data['email']],
                fail_silently=False,
                )
        return redirect('/')

class ValidationView(TemplateView):
    template_name = "base.html"
    
    def get_context_data(self, **kwargs):
        context = super(ValidationView, self).get_context_data(**kwargs)
        token_string = context['token']
        token_qs = ValidationToken.objects.filter(token=token_string)
        token_object = token_qs.first()
        if token_object.token_type == 'v':
            user_qs = User.objects.filter(email=token_object.email)
            user = user_qs.first()
            user.is_active = True
            user.email_validated = True
            user.save()
            token_object.delete()
            redirect('/')
        return context
    '''
    def as_view(self, *kwargs):
        token_string = self.kwargs['token']
        token_object = ValidationToken.objects.get_object_or_404(token=token_string)
        if token_object.token_type == 'v':
            user = User.objects.get_object_or_404(email=token_object.email)
            user.is_active == True
            user.email_validated == True
            user.save()
            redirect('/')
    '''
    
class ChangePasswordView(FormView):
    template_name = "change_password.html"
    form_class = ChangePasswordForm
    
    def form_valid(self, form):
        #add error if password is incorrect..
        user = User.objects.get(username=self.request.user)
        if form.cleaned_data['new_password'] == form.cleaned_data['repeated_new_password']:
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            
        #     username=form.cleaned_data['username'],
        #     password=form.cleaned_data['password'],
        #     first_name=form.cleaned_data['first_name'],
        #     last_name=form.cleaned_data['last_name'],
        #     email=form.cleaned_data['email'],
        #     birth_date=form.cleaned_data['birth_date'],
        #     avatar=form.cleaned_data['avatar'],
        #     is_active=False,
        #     )
        # user.save()
        print(user.email)
        return redirect('/')
        
        
        