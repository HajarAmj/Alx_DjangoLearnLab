from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import DetailView
from .models import Book, Library
from .forms import BookForm


@login_required
def list_books(request):
    books = Book.objects.select_related('author').all()
    return render(request, 'relationship_app/list_books.html', {'books': books})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('list_books')
    else:
        form = AuthenticationForm()
    return render(request, 'relationship_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return render(request, 'relationship_app/logout.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})


class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'


def role_check(role):
    def check(user):
        return hasattr(user, 'userprofile') and user.userprofile.role == role
    return check


@user_passes_test(role_check('Admin'))
def admin_view(request):
    return render(request, 'relationship_app/admin_view.html')


@user_passes_test(role_check('Librarian'))
def librarian_view(request):
    return render(request, 'relationship_app/librarian_view.html')


@user_passes_test(role_check('Member'))
def member_view(request):
    return render(request, 'relationship_app/member_view.html')


@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_books')
    else:
        form = BookForm()
    return render(request, 'relationship_app/add_book.html', {'form': form})


@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('list_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/edit_book.html', {'form': form, 'book': book})


@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('list_books')
    return render(request, 'relationship_app/delete_book.html', {'book': book})







