from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class Tweet(models.Model):
    class Meta:
        ordering = ['-created']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    content = models.CharField(max_length=140, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class Relationship(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')

class User(AbstractUser):
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email_validated = models.BooleanField(default=False)

    def follow(self, twitter_profile):
        try:
            Relationship.objects.get(follower=self, following=twitter_profile)
        except Relationship.DoesNotExist:
            Relationship.objects.create(
                follower=self, following=twitter_profile)

    def unfollow(self, twitter_profile):
        try:
            rel = Relationship.objects.get(
                follower=self, following=twitter_profile)
        except Relationship.DoesNotExist:
            return
        rel.delete()

    def is_following(self, twitter_profile):
        return Relationship.objects.filter(
            follower=self, following=twitter_profile).exists()

    @property
    def following(self):
        return [rel.following for rel in
                Relationship.objects.filter(follower=self)]

    @property
    def followers(self):
        return [rel.following for rel in
                Relationship.objects.filter(following=self)]

    @property
    def count_following(self):
        return Relationship.objects.filter(follower=self).count()

    @property
    def count_followers(self):
        return Relationship.objects.filter(following=self).count()

class ValidationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    
    # @property
    # def email(self):
    #     return User.objects.filter(email=self).email
        
    token = models.CharField(max_length=16, blank=True)
    token_type = models.CharField(max_length=1, null=True, blank=True)