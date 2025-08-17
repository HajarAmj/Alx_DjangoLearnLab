from datetime import date
from rest_framework import serializers
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    Serializes the Book model.

    Includes custom validation to ensure publication_year is not in the future.
    """
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']

    def validate_publication_year(self, value: int) -> int:
        """
        Ensure the publication year is <= the current year.
        """
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"publication_year cannot be in the future ({value} > {current_year})."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializes the Author model and nests related books.

    The 'books' field uses the reverse relationship defined by
    Book.author (related_name='books'). By marking it read_only=True,
    we serialize related books but do not accept nested writes here.
    """
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
