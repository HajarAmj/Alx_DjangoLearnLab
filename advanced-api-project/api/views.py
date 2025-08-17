from typing import Any
from django.db.models import QuerySet
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework

from .models import Book
from .serializers import BookSerializer


class BookListView(generics.ListAPIView):
   """
    List all books with advanced query capabilities:
    - Filtering: /api/books/?title=Python
    - Searching: /api/books/?search=Python
    - Ordering: /api/books/?ordering=-publication_year
    Multiple query params can be combined.
    """
    queryset: QuerySet[Book] = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author__name']
    ordering_fields = ['publication_year', 'title']
    ordering = ['title']


class BookDetailView(generics.RetrieveAPIView):
    """
    GET /api/books/<pk>/
    - Public, read-only single record.
    """
    queryset: QuerySet[Book] = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class BookCreateView(generics.CreateAPIView):
    """
    POST /api/books/create/
    - Authenticated users can create.
    - Accepts JSON and form-data (useful for Postman).
    - Extra rule: (title, author) pair must be unique.
    """
    queryset: QuerySet[Book] = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_create(self, serializer: BookSerializer) -> None:
        title = serializer.validated_data['title']
        author = serializer.validated_data['author']
        if Book.objects.filter(title=title, author=author).exists():
            raise ValidationError(
                {"non_field_errors": ["This author already has a book with the same title."]}
            )
        serializer.save()


class BookUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /api/books/<pk>/update/
    - Authenticated users can update.
    - Accepts JSON and form-data.
    - Keeps the same uniqueness rule as create.
      (We exclude self when checking duplicates.)
    """
    queryset: QuerySet[Book] = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_update(self, serializer: BookSerializer) -> None:
        instance: Book = self.get_object()
        title = serializer.validated_data.get('title', instance.title)
        author = serializer.validated_data.get('author', instance.author)
        if Book.objects.exclude(pk=instance.pk).filter(title=title, author=author).exists():
            raise ValidationError(
                {"non_field_errors": ["This author already has a book with the same title."]}
            )
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/books/<pk>/delete/
    - Authenticated users can delete.
    """
    queryset: QuerySet[Book] = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

