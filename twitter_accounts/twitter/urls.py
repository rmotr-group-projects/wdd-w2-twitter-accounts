from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login', auth_views.login, {'template_name': 'login.html'}),
    url(r'^logout', views.logout),

    url(r'^follow', views.follow),
    url(r'^unfollow', views.unfollow),

    url(r'^profile', views.profile),

    url(r'^register', views.RegisterView.as_view()),

    url(r'^dashboard', views.DashboardView.as_view()),

    url(r'^users/reset-password', views.ResetPasswordView.as_view()),
    url(r'^users/change-password', views.ChangePasswordView.as_view()),
    url(r'^users/confirm-reset-password/(?P<validation_token>[\d\w]+)', views.ConfirmResetPasswordView.as_view()),
    url(r'^users/validate/(?P<validation_token>[\d\w]+)', views.ValidateView.as_view()),

    url(r'^tweet/(?P<tweet_id>\d+)/delete', views.delete_tweet),
    url(r'^(?P<username>\w+)$', views.home),
    url(r'^$', views.home),
    # media files
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
]
