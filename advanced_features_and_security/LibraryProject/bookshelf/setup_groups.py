from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookshelf.models import Book, Library, BookReview


class Command(BaseCommand):
    help = 'Create groups with permissions for the bookshelf application'

    def handle(self, *args, **options):
        # Create groups
        editors_group, created = Group.objects.get_or_create(name='Editors')
        viewers_group, created = Group.objects.get_or_create(name='Viewers')  
        admins_group, created = Group.objects.get_or_create(name='Admins')

        # Get content types for our models
        book_ct = ContentType.objects.get_for_model(Book)
        library_ct = ContentType.objects.get_for_model(Library)
        review_ct = ContentType.objects.get_for_model(BookReview)

        # Get permissions for Book model
        book_permissions = Permission.objects.filter(content_type=book_ct)
        can_view_book = Permission.objects.get(content_type=book_ct, codename='can_view')
        can_create_book = Permission.objects.get(content_type=book_ct, codename='can_create')
        can_edit_book = Permission.objects.get(content_type=book_ct, codename='can_edit')
        can_delete_book = Permission.objects.get(content_type=book_ct, codename='can_delete')

        # Get permissions for Library model
        library_permissions = Permission.objects.filter(content_type=library_ct)
        can_view_library = Permission.objects.get(content_type=library_ct, codename='can_view')
        can_create_library = Permission.objects.get(content_type=library_ct, codename='can_create')
        can_edit_library = Permission.objects.get(content_type=library_ct, codename='can_edit')
        can_delete_library = Permission.objects.get(content_type=library_ct, codename='can_delete')

        # Get permissions for BookReview model
        review_permissions = Permission.objects.filter(content_type=review_ct)
        can_view_review = Permission.objects.get(content_type=review_ct, codename='can_view')
        can_create_review = Permission.objects.get(content_type=review_ct, codename='can_create')
        can_edit_review = Permission.objects.get(content_type=review_ct, codename='can_edit')
        can_delete_review = Permission.objects.get(content_type=review_ct, codename='can_delete')

        # Assign permissions to Viewers group
        viewers_group.permissions.clear()
        viewers_group.permissions.add(
            can_view_book,
            can_view_library, 
            can_view_review
        )

        # Assign permissions to Editors group
        editors_group.permissions.clear()
        editors_group.permissions.add(
            can_view_book,
            can_create_book,
            can_edit_book,
            can_view_library,
            can_create_library,
            can_edit_library,
            can_view_review,
            can_create_review,
            can_edit_review
        )

        # Assign permissions to Admins group (all permissions)
        admins_group.permissions.clear()
        admins_group.permissions.add(*book_permissions)
        admins_group.permissions.add(*library_permissions) 
        admins_group.permissions.add(*review_permissions)

        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and assigned permissions:')
        )
        self.stdout.write(f'- Viewers: {viewers_group.permissions.count()} permissions')
        self.stdout.write(f'- Editors: {editors_group.permissions.count()} permissions')
        self.stdout.write(f'- Admins: {admins_group.permissions.count()} permissions')

        # Display permission details
        self.stdout.write('\nGroup permissions:')
        
        self.stdout.write('\nViewers Group:')
        for perm in viewers_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')

        self.stdout.write('\nEditors Group:')
        for perm in editors_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')

        self.stdout.write('\nAdmins Group:')
        for perm in admins_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')
