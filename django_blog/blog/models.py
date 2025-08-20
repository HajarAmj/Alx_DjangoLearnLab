from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
        on_delete=models.CASCADE,
        related_name='posts'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)


    def __str__(self):
        return f"Profile({self.user.username})"


class Comment(models.Model):
    post = models.ForeignKey(
        'Post', # or replace with the correct app label if Post is elsewhere
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['created_at'] # oldest first; change to ['-created_at'] for newest first


    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})
