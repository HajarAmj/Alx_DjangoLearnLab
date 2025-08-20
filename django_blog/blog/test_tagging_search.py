from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Post, Tag

User = get_user_model()

class TaggingSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        self.p1 = Post.objects.create(title='Django tips', content='Learn Django', author=self.user)
        self.p2 = Post.objects.create(title='Python tricks', content='Useful Python', author=self.user)
        t_python = Tag.objects.create(name='python')
        t_django = Tag.objects.create(name='django')
        self.p1.tags.add(t_django, t_python)
        self.p2.tags.add(t_python)

    def test_posts_by_tag_view(self):
        resp = self.client.get(reverse('posts_by_tag', kwargs={'tag_slug': 'python'}))
        self.assertContains(resp, 'Django tips')
        self.assertContains(resp, 'Python tricks')

    def test_search_by_title(self):
        resp = self.client.get(reverse('search'), {'q': 'Django'})
        self.assertContains(resp, 'Django tips')
        self.assertNotContains(resp, 'Python tricks')

    def test_search_by_tag(self):
        resp = self.client.get(reverse('search'), {'q': 'python'})
        self.assertContains(resp, 'Django tips')
        self.assertContains(resp, 'Python tricks')
