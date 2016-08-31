from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login', auth_views.login, {'template_name': 'login.html'}),
    url(r'^logout', views.logout),
    #url(r'^follow', views.follow),
    #url(r'^unfollow', views.unfollow),
    url(r'^register', views.register),
    url(r'^users/validate/(?P<token>\w+)$', views.validate_user),
    url(r'^change-password', views.change_password),
    #url(r'^tweet/(?P<tweet_id>\d+)/delete', views.delete_tweet),
    url(r'^(?P<username>\w+)$', views.home),
    url(r'^$', views.home),
    # media files
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
]
