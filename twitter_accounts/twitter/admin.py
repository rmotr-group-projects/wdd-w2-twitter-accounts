from django.contrib import admin

from .models import Tweet, Relationship, User, ValidationToken

admin.site.register(Tweet)
admin.site.register(Relationship)
admin.site.register(User)
admin.site.register(ValidationToken)
