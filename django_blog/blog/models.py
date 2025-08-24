from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

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

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Normalize whitespace
        self.name = self.name.strip()
        if not self.slug:
            # create a slug from the name
            base = slugify(self.name)
            slug_candidate = base
            n = 1
            # ensure unique slug
            while Tag.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                n += 1
                slug_candidate = f"{base}-{n}"
            self.slug = slug_candidate
        super().save(*args, **kwargs)


# Example Post model (you likely already have this — just add the `tags` field).
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add the many-to-many relation
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
