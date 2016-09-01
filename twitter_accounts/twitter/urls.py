from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^login', auth_views.login, {'template_name': 'login.html'}),
    url(r'^logout', views.logout),
    url(r'^register', TemplateView.as_view(template_name="register.html")),
    url(r'^follow', views.follow),
    url(r'^unfollow', views.unfollow),
    url(r'^profile', views.profile),
    url(r'^tweet/(?P<tweet_id>\d+)/delete', views.delete_tweet),
    url(r'^(?P<username>\w+)$', views.home),
    url(r'^$', views.home),
    # media files
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
]
