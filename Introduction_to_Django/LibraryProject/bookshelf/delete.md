# Delete Operation

```python
from bookshelf.models import Book

book.delete()
print(Book.objects.all())
# Output:
# <QuerySet []>

