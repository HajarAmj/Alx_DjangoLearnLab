from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    GET /api/books/ -> list all Book instances
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Book:
    - list:   GET  /books_all/
    - create: POST /books_all/
    - retrieve: GET /books_all/{pk}/
    - update: PUT /books_all/{pk}/
    - partial_update: PATCH /books_all/{pk}/
    - destroy: DELETE /books_all/{pk}/
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
