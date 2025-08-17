from django.db import models

class Author(models.Model):
    """
    Author represents a writer who may have written one or more books.
    
    Fields:
        name (CharField): The author's display name.
    
    Relationship:
        One Author -> Many Book (via Book.author)
    """
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """
    Book represents a published work.

    Fields:
        title (CharField): The title of the book.
        publication_year (IntegerField): The year the book was published.
        author (ForeignKey -> Author): Links each Book to exactly one Author.
            related_name='books' lets us access an author's books via author.books
            and supports nested serialization cleanly.
    """
    title = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.publication_year})"

