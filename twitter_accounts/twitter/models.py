import random
import string

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


def get_hash_token(hash_length=16):
    """Generates random 16 char lowercase string with numbers and lowercase letters"""
    hash_seed = string.ascii_lowercase + string.digits
    hash_string = ''
    for x in random.sample(hash_seed, hash_length):
        hash_string += x
    return hash_string

def validate_hash_token(value):
    """
    Raises a ValidationError if hash token has not length 16 or contains invalid
    characters
    """
    valid_chars = set(string.ascii_letters + string.digits)
    if not set(value).issubset(valid_chars) or len(value) != 16:
        raise ValidationError(
            'Hash token must be a string containing 16 alphanumeric lowercase characters')


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
    email = models.EmailField()
    token = models.CharField(max_length=16, default=get_hash_token,
                             validators=[validate_hash_token])

    class Meta:
        unique_together = (("email", "token"))

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ValidationToken, self).save(*args, **kwargs)
