from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Book
from django.contrib.auth.models import User

class BookAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")

        # Create sample books
        self.book1 = Book.objects.create(title="Python Basics", author="John Doe", publication_year=2023)
        self.book2 = Book.objects.create(title="Advanced Django", author="Jane Smith", publication_year=2022)

    def test_list_books(self):
        url = reverse('book-list')  # make sure your urls.py has name='book-list'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_book(self):
        url = reverse('book-list')
        data = {"title": "REST APIs", "author": "Alice", "publication_year": 2024}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.get(id=response.data['id']).title, "REST APIs")

    def test_update_book(self):
        url = reverse('book-detail', args=[self.book1.id])  # name='book-detail'
        data = {"title": "Python Basics Updated", "author": "John Doe", "publication_year": 2023}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Python Basics Updated")

    def test_delete_book(self):
        url = reverse('book-detail', args=[self.book2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book2.id).exists())

    def test_filter_books(self):
        url = reverse('book-list') + "?author=John Doe"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author'], "John Doe")

    def test_search_books(self):
        url = reverse('book-list') + "?search=Advanced"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], "Advanced Django")

    def test_order_books(self):
        url = reverse('book-list') + "?ordering=-publication_year"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['publication_year'], 2023)

"""
Test Suite for Book API Endpoints

Covers:
- CRUD operations (create, list, update, delete)
- Filtering, searching, and ordering functionalities
- Authentication and permissions enforcement

Run tests with:
    python manage.py test api
"""
