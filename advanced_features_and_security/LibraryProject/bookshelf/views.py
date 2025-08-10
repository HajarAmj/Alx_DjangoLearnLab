from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Book, Library, BookReview
from .forms import BookForm, LibraryForm, BookReviewForm


# Book Views with Permission Checks
class BookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all books - requires can_view permission"""
    model = Book
    template_name = 'bookshelf/book_list.html'
    context_object_name = 'books'
    permission_required = 'bookshelf.can_view'

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to view books.")
        return redirect('home')


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_detail_view(request, pk):
    """View book details - requires can_view permission"""
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    context = {
        'book': book,
        'reviews': reviews,
        'can_edit': request.user.has_perm('bookshelf.can_edit'),
        'can_delete': request.user.has_perm('bookshelf.can_delete'),
        'can_create_review': request.user.has_perm('bookshelf.can_create'),
    }
    return render(request, 'bookshelf/book_detail.html', context)


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create new book - requires can_create permission"""
    model = Book
    form_class = BookForm
    template_name = 'bookshelf/book_form.html'
    success_url = reverse_lazy('book_list')
    permission_required = 'bookshelf.can_create'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Book created successfully!')
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to create books.")
        return redirect('book_list')


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update book - requires can_edit permission"""
    model = Book
    form_class = BookForm
    template_name = 'bookshelf/book_form.html'
    permission_required = 'bookshelf.can_edit'

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit books.")
        return redirect('book_list')


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete book - requires can_delete permission"""
    model = Book
    template_name = 'bookshelf/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    permission_required = 'bookshelf.can_delete'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Book deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete books.")
        return redirect('book_list')


# Library Views with Permission Checks
@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def library_list_view(request):
    """List all libraries - requires can_view permission"""
    libraries = Library.objects.all()
    context = {
        'libraries': libraries,
        'can_create': request.user.has_perm('bookshelf.can_create'),
        'can_edit': request.user.has_perm('bookshelf.can_edit'),
        'can_delete': request.user.has_perm('bookshelf.can_delete'),
    }
    return render(request, 'bookshelf/library_list.html', context)


@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def library_create_view(request):
    """Create new library - requires can_create permission"""
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            library = form.save()
            messages.success(request, f'Library "{library.name}" created successfully!')
            return redirect('library_list')
    else:
        form = LibraryForm()
    
    return render(request, 'bookshelf/library_form.html', {'form': form})


@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def library_edit_view(request, pk):
    """Edit library - requires can_edit permission"""
    library = get_object_or_404(Library, pk=pk)
    
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            library = form.save()
            messages.success(request, f'Library "{library.name}" updated successfully!')
            return redirect('library_list')
    else:
        form = LibraryForm(instance=library)
    
    return render(request, 'bookshelf/library_form.html', {'form': form, 'library': library})


# Book Review Views with Permission Checks
@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def create_review_view(request, book_id):
    """Create book review - requires can_create permission"""
    book = get_object_or_404(Book, id=book_id)
    
    # Check if user already reviewed this book
    if BookReview.objects.filter(book=book, reviewer=request.user).exists():
        messages.warning(request, 'You have already reviewed this book.')
        return redirect('book_detail', pk=book_id)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('book_detail', pk=book_id)
    else:
        form = BookReviewForm()
    
    return render(request, 'bookshelf/review_form.html', {'form': form, 'book': book})


@login_required
def edit_review_view(request, review_id):
    """Edit book review - user can edit their own review or need can_edit permission"""
    review = get_object_or_404(BookReview, id=review_id)
    
    # Check if user can edit (owns the review or has can_edit permission)
    if review.reviewer != request.user and not request.user.has_perm('bookshelf.can_edit'):
        messages.error(request, "You don't have permission to edit this review.")
        return redirect('book_detail', pk=review.book.pk)
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('book_detail', pk=review.book.pk)
    else:
        form = BookReviewForm(instance=review)
    
    return render(request, 'bookshelf/review_form.html', {'form': form, 'review': review})


@login_required
def delete_review_view(request, review_id):
    """Delete book review - user can delete their own review or need can_delete permission"""
    review = get_object_or_404(BookReview, id=review_id)
    
    # Check if user can delete (owns the review or has can_delete permission)
    if review.reviewer != request.user and not request.user.has_perm('bookshelf.can_delete'):
        messages.error(request, "You don't have permission to delete this review.")
        return redirect('book_detail', pk=review.book.pk)
    
    if request.method == 'POST':
        book_pk = review.book.pk
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('book_detail', pk=book_pk)
    
    return render(request, 'bookshelf/review_confirm_delete.html', {'review': review})


# Custom Permission Check Function
def user_can_perform_action(user, action):
    """
    Helper function to check if user has permission for specific action
    Actions: 'view', 'create', 'edit', 'delete'
    """
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
