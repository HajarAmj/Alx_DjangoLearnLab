from django.contrib.auth.models import AbstractUser
from django.db import models

def user_profile_upload_to(instance, filename):
    return f'profiles/{instance.username}/{filename}'

class User(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_upload_to, blank=True, null=True)
    # 'followers' is the set of users who follow THIS user
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def followers_count(self) -> int:
        return self.followers.count()

    def following_count(self) -> int:
        return self.following.count()

    def __str__(self):
        return self.username
