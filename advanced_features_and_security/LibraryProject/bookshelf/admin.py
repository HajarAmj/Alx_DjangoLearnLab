from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from bookshelf.models import CustomUser
from django.utils.translation import gettext_lazy as _
from bookshelf.models import CustomUser, UserProfile
from django.contrib.auth.models import User, Group
from .models import Book, Library, BookReview


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'profile_photo')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'date_of_birth', 'profile_photo'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')

class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model"""
    list_display = ['title', 'author', 'publication_year', 'isbn', 'created_by', 'created_at']
    list_filter = ['publication_year', 'created_at', 'author']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'publication_year', 'isbn')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Set created_by to current user if not set"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class LibraryAdmin(admin.ModelAdmin):
    """Admin configuration for Library model"""
    list_display = ['name', 'location', 'book_count', 'created_at']
    search_fields = ['name', 'location']
    filter_horizontal = ['books']  # Better UI for many-to-many field
    readonly_fields = ['created_at']

    def book_count(self, obj):
        """Display number of books in library"""
        return obj.books.count()
    book_count.short_description = 'Number of Books'


class BookReviewAdmin(admin.ModelAdmin):
    """Admin configuration for BookReview model"""
    list_display = ['book', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'reviewer__username', 'comment']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Review Information', {
            'fields': ('book', 'reviewer', 'rating', 'comment')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(UserAdmin):
    """Enhanced User admin with group management"""
    list_display = UserAdmin.list_display + ('get_groups',)
    
    def get_groups(self, obj):
        """Display user's groups"""
        return ', '.join([group.name for group in obj.groups.all()]) or 'None'
    get_groups.short_description = 'Groups'

    # Add groups to the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Permissions & Groups', {
            'fields': ('groups', 'user_permissions'),
        }),
    )


class GroupAdmin(admin.ModelAdmin):
    """Enhanced Group admin"""
    list_display = ['name', 'get_permission_count', 'get_user_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']

    def get_permission_count(self, obj):
        """Display number of permissions in group"""
        return obj.permissions.count()
    get_permission_count.short_description = 'Permissions'

    def get_user_count(self, obj):
        """Display number of users in group"""
        return obj.user_set.count()
    get_user_count.short_description = 'Users'

admin.site.register(Book)
admin.site.register(Library)  
admin.site.register(BookReview)
admin.site.site_header = 'Library Management System'
admin.site.site_title = 'Library Admin'
admin.site.index_title = 'Welcome to Library Administration'
