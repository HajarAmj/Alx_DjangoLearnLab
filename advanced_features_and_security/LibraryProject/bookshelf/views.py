from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.utils.html import escape
from django.core.paginator import Paginator
from django.db import transaction
import logging
from .forms import ExampleForm, BookForm, SearchForm
from .models import Book, Library, BookReview
from .forms import BookForm, LibraryForm, BookReviewForm, BookSearchForm

security_logger = logging.getLogger('django.security')

# Book Views with Permission Checks
class BookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all books with secure search functionality.
    
    Security features:
    - Permission-based access control
    - Safe database queries using Django ORM
    - Input sanitization for search queries
    - XSS protection through template escaping"""

    """List all books - requires can_view permission"""
    model = Book
    template_name = 'bookshelf/book_list.html'
    context_object_name = 'books'
    permission_required = 'bookshelf.can_view'
    aginate_by = 20 

    def handle_no_permission(self):
        """Log security events and redirect unauthorized users."""
        security_logger.warning(
            f"Unauthorized access attempt to book list by user: {self.request.user} "
            f"from IP: {self.request.META.get('REMOTE_ADDR')}"
        )
        messages.error(self.request, "You don't have permission to view books.")
        return redirect('home')

   def get_queryset(self):
        """
        Secure queryset with search functionality.
        Uses Django ORM to prevent SQL injection.
        """
        queryset = Book.objects.all().select_related()
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            # Validate search query length to prevent abuse
            if len(search_query) > 100:
                security_logger.warning(
                    f"Excessive search query length from user {self.request.user}: {len(search_query)} chars"
                )
                messages.error(self.request, 'Search query is too long.')
                return queryset.none()
            
            # Use Django ORM Q objects for safe database queries
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
        
        return queryset.order_by('title', 'author')

    def get_context_data(self, **kwargs):
        """Add additional context with security considerations."""
        context = super().get_context_data(**kwargs)
        
        # Add search form with validation
        search_query = self.request.GET.get('search', '')
        context['search_form'] = BookSearchForm(initial={'search': search_query})
        context['search_query'] = escape(search_query)  # Escape for safe display
        
        # Add permission context
        context.update({
            'can_create': self.request.user.has_perm('bookshelf.can_create'),
            'can_edit': self.request.user.has_perm('bookshelf.can_edit'),
            'can_delete': self.request.user.has_perm('bookshelf.can_delete'),
        })
        
        return context

@csrf_protect
def example_form_view(request):
    """
    View to handle ExampleForm submission securely.
    """
    if request.method == "POST":
        form = ExampleForm(request.POST)
        if form.is_valid():
            # Safe handling of cleaned data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Here, you'd normally save or process the data securely
            return redirect('bookshelf:book_list')
    else:
        form = ExampleForm()
    return render(request, 'bookshelf/form_example.html', {'form': form})

@csrf_protect
@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_detail_view(request, pk):
     """
    View book details with security protections.
    
    Security features:
    - CSRF protection
    - Safe object retrieval
    - Permission checking
    - XSS prevention through escaping
    """
    try:
        # Use get_object_or_404 for safe object retrieval
        book = get_object_or_404(Book, pk=pk)
        
        # Get reviews with safe querying
        reviews = book.reviews.select_related('reviewer').all()
        
        # Check permissions securely
        user_permissions = {
            'can_edit': request.user.has_perm('bookshelf.can_edit'),
            'can_delete': request.user.has_perm('bookshelf.can_delete'),
            'can_create_review': request.user.has_perm('bookshelf.can_create'),
        }
        
        context = {
            'book': book,
            'reviews': reviews,
            **user_permissions,
        }
        
        return render(request, 'bookshelf/book_detail.html', context)
        
    except Exception as e:
        security_logger.error(f"Error in book_detail_view: {e}")
        messages.error(request, "An error occurred while loading the book details.")
        return redirect('book_list')


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create new book with comprehensive security measures.
    
    Security features:
    - CSRF protection (automatic with Django forms)
    - Permission-based access control
    - Form validation and sanitization
    - Transaction safety"""
    model = Book
    form_class = BookForm
    template_name = 'bookshelf/book_form.html'
    success_url = reverse_lazy('book_list')
    permission_required = 'bookshelf.can_create'

    @transaction.atomic
    def form_valid(self, form):
        """
        Process valid form with transaction safety.
        """
        try:
            form.instance.created_by = self.request.user
            response = super().form_valid(form)
            
            # Log successful creation
            security_logger.info(f"Book created by user {self.request.user}: {form.instance.title}")
            messages.success(self.request, 'Book created successfully!')
            
            return response
            
        except ValidationError as e:
            security_logger.warning(f"Book creation validation error by user {self.request.user}: {e}")
            form.add_error(None, "Invalid data provided. Please check your input.")
            return self.form_invalid(form)
        
        except Exception as e:
            security_logger.error(f"Book creation error by user {self.request.user}: {e}")
            messages.error(self.request, "An error occurred while creating the book.")
            return redirect('book_list')

    def handle_no_permission(self):
        """Log unauthorized access attempts."""
        security_logger.warning(f"Unauthorized book creation attempt by user: {self.request.user}")
        messages.error(self.request, "You don't have permission to create books.")
        return redirect('book_list')


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
     """Update book with security validations.
    
    Security features:
    - Object-level permission checking
    - CSRF protection
    - Input validation
    - Safe object retrieval"""
    model = Book
    form_class = BookForm
    template_name = 'bookshelf/book_form.html'
    permission_required = 'bookshelf.can_edit'

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})

     @transaction.atomic
    def form_valid(self, form):
        """Process form updates with security logging."""
        try:
            response = super().form_valid(form)
            
            # Log successful update
            security_logger.info(f"Book updated by user {self.request.user}: {form.instance.title}")
            messages.success(self.request, 'Book updated successfully!')
            
            return response
            
        except ValidationError as e:
            security_logger.warning(f"Book update validation error by user {self.request.user}: {e}")
            form.add_error(None, "Invalid data provided. Please check your input.")
            return self.form_invalid(form)

    def handle_no_permission(self):
        """Log unauthorized access attempts."""
        security_logger.warning(f"Unauthorized book edit attempt by user: {self.request.user}")
        messages.error(self.request, "You don't have permission to edit books.")
        return redirect('book_list')


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete book with proper security checks.
    
    Security features:
    - Permission-based access control
    - CSRF protection
    - POST-only deletion
    - Safe object retrieval"""
    model = Book
    template_name = 'bookshelf/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    permission_required = 'bookshelf.can_delete'

     @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Secure deletion with logging."""
        try:
            book_title = escape(self.get_object().title)  # Escape for safe logging
            response = super().delete(request, *args, **kwargs)
            
            # Log successful deletion
            security_logger.info(f"Book deleted by user {request.user}: {book_title}")
            messages.success(self.request, f'Book "{book_title}" deleted successfully!')
            
            return response
            
        except Exception as e:
            security_logger.error(f"Book deletion error by user {request.user}: {e}")
            messages.error(self.request, 'An error occurred while deleting the book.')
            return redirect('book_list')

    def handle_no_permission(self):
        """Log unauthorized access attempts."""
        security_logger.warning(f"Unauthorized book deletion attempt by user: {self.request.user}")
        messages.error(self.request, "You don't have permission to delete books.")
        return redirect('book_list')


@csrf_protect
@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def library_list_view(request):
    """List all libraries with security protections.
    
    Security features:
    - CSRF protection
    - Permission checking
    - Safe database queries"""
    libraries = Library.objects.all().prefetch_related('books')
    context = {
        'libraries': libraries,
        'can_create': request.user.has_perm('bookshelf.can_create'),
        'can_edit': request.user.has_perm('bookshelf.can_edit'),
        'can_delete': request.user.has_perm('bookshelf.can_delete'),
    }
    return render(request, 'bookshelf/library_list.html', context)

except Exception as e:
    security_logger.error(f"Error in library_list_view: {e}")
    messages.error(request, "An error occurred while loading libraries.")
    return redirect('home')

@csrf_protect
@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
@require_http_methods(["GET", "POST"])
def library_create_view(request):
     """Create new library with security validations.
    
    Security features:
    - CSRF protection
    - HTTP method restriction
    - Form validation
    - Transaction safety"""
     if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    library = form.save()
                    security_logger.info(f"Library created by user {request.user}: {library.name}")
                    messages.success(request, f'Library "{escape(library.name)}" created successfully!')
                    return redirect('library_list')
                    
            except ValidationError as e:
                security_logger.warning(f"Library creation validation error by user {request.user}: {e}")
                form.add_error(None, "Invalid data provided.")
            except Exception as e:
                security_logger.error(f"Library creation error by user {request.user}: {e}")
                messages.error(request, "An error occurred while creating the library.")
        else:
            security_logger.info(f"Library form validation failed for user {request.user}: {form.errors}")
    else:
        form = LibraryForm()
    
    return render(request, 'bookshelf/library_form.html', {'form': form})


@csrf_protect
@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
@require_http_methods(["GET", "POST"])
def library_edit_view(request, pk):
    """
    Edit library with security validations.
    
    Security features:
    - Safe object retrieval
    - CSRF protection
    - Input validation
    - Transaction safety
    """
    library = get_object_or_404(Library, pk=pk)
    
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            try:
                with transaction.atomic():
                    library = form.save()
                    security_logger.info(f"Library updated by user {request.user}: {library.name}")
                    messages.success(request, f'Library "{escape(library.name)}" updated successfully!')
                    return redirect('library_list')
                    
            except ValidationError as e:
                security_logger.warning(f"Library update validation error by user {request.user}: {e}")
                form.add_error(None, "Invalid data provided.")
            except Exception as e:
                security_logger.error(f"Library update error by user {request.user}: {e}")
                messages.error(request, "An error occurred while updating the library.")
    else:
        form = LibraryForm(instance=library)
    
    return render(request, 'bookshelf/library_form.html', {'form': form, 'library': library})

# =============================================================================
# BOOK REVIEW VIEWS WITH ENHANCED SECURITY
# =============================================================================

@csrf_protect
@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
@require_http_methods(["GET", "POST"])
def create_review_view(request, book_id):
    """
    Create book review with security protections.
    
    Security features:
    - CSRF protection
    - Permission checking
    - Duplicate prevention
    - Input validation
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Check if user already reviewed this book (prevent duplicate reviews)
    if BookReview.objects.filter(book=book, reviewer=request.user).exists():
        messages.warning(request, 'You have already reviewed this book.')
        return redirect('book_detail', pk=book_id)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    review = form.save(commit=False)
                    review.book = book
                    review.reviewer = request.user
                    review.save()
                    
                    security_logger.info(f"Review created by user {request.user} for book {book.title}")
                    messages.success(request, 'Review submitted successfully!')
                    return redirect('book_detail', pk=book_id)
                    
            except ValidationError as e:
                security_logger.warning(f"Review creation validation error by user {request.user}: {e}")
                form.add_error(None, "Invalid review data.")
            except Exception as e:
                security_logger.error(f"Review creation error by user {request.user}: {e}")
                messages.error(request, "An error occurred while submitting your review.")
        else:
            security_logger.info(f"Review form validation failed for user {request.user}: {form.errors}")
    else:
        form = BookReviewForm()
    
    return render(request, 'bookshelf/review_form.html', {'form': form, 'book': book})

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def edit_review_view(request, review_id):
    """
    Edit book review with object-level permissions.
    
    Security features:
    - Object-level permission checking
    - CSRF protection
    - Safe object retrieval
    """
    review = get_object_or_404(BookReview, id=review_id)
    
    # Check if user can edit (owns the review or has can_edit permission)
    if review.reviewer != request.user and not request.user.has_perm('bookshelf.can_edit'):
        security_logger.warning(
            f"Unauthorized review edit attempt by user {request.user} for review {review_id}"
        )
        messages.error(request, "You don't have permission to edit this review.")
        return redirect('book_detail', pk=review.book.pk)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST, instance=review)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    security_logger.info(f"Review updated by user {request.user}: review {review_id}")
                    messages.success(request, 'Review updated successfully!')
                    return redirect('book_detail', pk=review.book.pk)
                    
            except ValidationError as e:
                security_logger.warning(f"Review update validation error by user {request.user}: {e}")
                form.add_error(None, "Invalid review data.")
        else:
            security_logger.info(f"Review update form validation failed for user {request.user}: {form.errors}")
    else:
        form = BookReviewForm(instance=review)
    
    return render(request, 'bookshelf/review_form.html', {'form': form, 'review': review})

@csrf_protect
@login_required
@require_POST
def delete_review_view(request, review_id):
    """
    Delete book review with proper security checks.
    
    Security features:
    - POST-only deletion
    - Object-level permission checking
    - CSRF protection
    - Transaction safety
    """
    review = get_object_or_404(BookReview, id=review_id)
    
    # Check if user can delete (owns the review or has can_delete permission)
    if review.reviewer != request.user and not request.user.has_perm('bookshelf.can_delete'):
        security_logger.warning(
            f"Unauthorized review deletion attempt by user {request.user} for review {review_id}"
        )
        messages.error(request, "You don't have permission to delete this review.")
        return redirect('book_detail', pk=review.book.pk)
    
    try:
        book_pk = review.book.pk
        with transaction.atomic():
            review.delete()
            security_logger.info(f"Review deleted by user {request.user}: review {review_id}")
            messages.success(request, 'Review deleted successfully!')
            return redirect('book_detail', pk=book_pk)
            
    except Exception as e:
        security_logger.error(f"Review deletion error by user {request.user}: {e}")
        messages.error(request, "An error occurred while deleting the review.")
        return redirect('book_detail', pk=review.book.pk)

# =============================================================================
# API ENDPOINTS WITH SECURITY
# =============================================================================

@csrf_protect
@login_required
@require_http_methods(["GET"])
def book_api(request):
    """
    Secure API endpoint for book data.
    
    Security features:
    - Authentication required
    - CSRF protection
    - Input validation
    - Rate limiting considerations
    """
    try:
        search_query = request.GET.get('q', '').strip()
        
        if search_query:
            # Validate search query length to prevent abuse
            if len(search_query) > 100:
                return JsonResponse({'error': 'Search query too long'}, status=400)
            
            # Use ORM for safe querying
            books = Book.objects.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query)
            )[:20]  # Limit results
        else:
            books = Book.objects.all()[:20]
        
        books_data = []
        for book in books:
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'published_date': book.published_date.isoformat() if book.published_date else None,
            })
        
        return JsonResponse({'books': books_data})
    
    except Exception as e:
        security_logger.error(f"API error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# =============================================================================
# UTILITY FUNCTIONS FOR SECURITY
# =============================================================================

def user_can_perform_action(user, action):
    """
    Helper function to check if user has permission for specific action.
    
    Security features:
    - Centralized permission checking
    - Input validation
    """
    if not user or not user.is_authenticated:
        return False
    
    permission_map = {
        'view': 'bookshelf.can_view',
        'create': 'bookshelf.can_create',
        'edit': 'bookshelf.can_edit',
        'delete': 'bookshelf.can_delete',
    }
    
    permission = permission_map.get(action)
    if permission:
        return user.has_perm(permission)
    
    return False

def log_security_event(request, event_type, details):
    """
    Utility function to log security events.
    
    Args:
        request: HTTP request object
        event_type: Type of security event
        details: Additional details about the event
    """
    security_logger.warning(
        f"Security Event - {event_type}: {details} | "
        f"User: {request.user} | IP: {request.META.get('REMOTE_ADDR')} | "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')} | "
        f"Path: {request.path}"
    )

def sanitize_input(input_string, max_length=255):
    """
    Utility function to sanitize user input.
    
    Args:
        input_string: The input to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove dangerous characters and limit length
    sanitized = escape(str(input_string).strip()[:max_length])
    return sanitized
