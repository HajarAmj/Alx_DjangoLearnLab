import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_models.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

# Query: All books by a specific author
def books_by_author(author_name):
    author = Author.objects.get(name=author_name)
    return Book.objects.filter(author=author)

# Query: List all books in a library
def books_in_library(library_name):
    library = Library.objects.get(name=library_name)
    return library.books.all()

# Query: Retrieve the librarian for a library
def librarian_of_library(library_name):
    library = Library.objects.get(name=library_name)
    return Librarian.objects.get(library=library)

# Sample usage
if __name__ == "__main__":
    print("Books by author John Doe:", books_by_author("John Doe"))
    print("Books in Library Central Library:", books_in_library("Central Library"))
    print("Librarian of Central Library:", librarian_of_library("Central Library"))
