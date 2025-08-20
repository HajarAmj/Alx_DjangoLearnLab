from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from blog.models import Post, Comment

User = get_user_model()

class CommentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.other = User.objects.create_user(username='bob', password='pass12345')
        self.post = Post.objects.create(title='Hello', content='World')

    def test_create_comment_requires_login(self):
        url = reverse('blog:comment_create', kwargs={'post_id': self.post.pk})
        resp = self.client.post(url, {'content': 'Hi'})
        self.assertNotEqual(resp.status_code, 200)

    def test_create_edit_delete_comment_by_author(self):
        self.client.login(username='alice', password='pass12345')
        create_url = reverse('blog:comment_create', kwargs={'post_id': self.post.pk})
        self.client.post(create_url, {'content': 'Nice post!'})
        comment = Comment.objects.get()

        # edit
        edit_url = reverse('blog:comment_edit', kwargs={'post_id': self.post.pk, 'pk': comment.pk})
        self.client.post(edit_url, {'content': 'Updated text'})
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated text')

        # delete
        delete_url = reverse('blog:comment_delete', kwargs={'post_id': self.post.pk, 'pk': comment.pk})
        self.client.post(delete_url)
        self.assertFalse(Comment.objects.exists())
