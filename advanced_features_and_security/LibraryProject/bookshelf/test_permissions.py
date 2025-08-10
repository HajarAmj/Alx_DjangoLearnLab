from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from bookshelf.models import Book, Library, BookReview


class Command(BaseCommand):
    help = 'Test permissions by creating test users and assigning them to groups'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users and testing permissions...\n')

        # Get or create groups
        viewers_group = Group.objects.get(name='Viewers')
        editors_group = Group.objects.get(name='Editors')
        admins_group = Group.objects.get(name='Admins')

        # Create test users
        test_users = [
            ('viewer_user', 'password123', viewers_group),
            ('editor_user', 'password123', editors_group),
            ('admin_user', 'password123', admins_group),
        ]

        for username, password, group in test_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.replace('_', ' ').title(),
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'Created user: {username}')
            else:
                self.stdout.write(f'User already exists: {username}')

            # Add user to group
            user.groups.clear()
            user.groups.add(group)
            self.stdout.write(f'Added {username} to {group.name} group')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('PERMISSION TESTING RESULTS')
        self.stdout.write('='*50)

        # Test permissions for each user
        for username, _, group in test_users:
            user = User.objects.get(username=username)
            self.stdout.write(f'\nTesting permissions for {username} ({group.name}):')
            
            # Test Book permissions
            self.stdout.write('  Book permissions:')
            self.stdout.write(f'    - can_view: {user.has_perm("bookshelf.can_view")}')
            self.stdout.write(f'    - can_create: {user.has_perm("bookshelf.can_create")}')
            self.stdout.write(f'    - can_edit: {user.has_perm("bookshelf.can_edit")}')
            self.stdout.write(f'    - can_delete: {user.has_perm("bookshelf.can_delete")}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST USER CREDENTIALS')
        self.stdout.write('='*50)
        self.stdout.write('Use these credentials to test the application:')
        self.stdout.write('Username: viewer_user | Password: password123 | Role: Viewer')
        self.stdout.write('Username: editor_user | Password: password123 | Role: Editor')  
        self.stdout.write('Username: admin_user  | Password: password123 | Role: Admin')

        # Create sample data for testing
        self.create_sample_data()

    def create_sample_data(self):
        """Create sample books for testing"""
        self.stdout.write('\nCreating sample data...')
        
        # Get admin user to create sample data
        admin_user = User.objects.get(username='admin_user')
        
        sample_books = [
            {
                'title': 'Django for Beginners',
                'author': 'William Vincent',
                'publication_year': 2022,
                'isbn': '9781735467221'
            },
            {
                'title': 'Python Crash Course',
                'author': 'Eric Matthes',
                'publication_year': 2019,
                'isbn': '9781593276034'
            },
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'publication_year': 2008,
                'isbn': '9780132350884'
            }
        ]

        for book_data in sample_books:
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults={
                    **book_data,
