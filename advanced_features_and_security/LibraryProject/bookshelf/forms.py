from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Book, Library, BookReview

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'date_of_birth', 'profile_photo', 'password1', 'password2']


class BookForm(forms.ModelForm):
    """Form for creating and editing books"""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year', 'isbn']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ISBN (13 digits)'
            }),
        }

    def clean_publication_year(self):
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 2030):
            raise forms.ValidationError("Please enter a valid publication year.")
        return year

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and len(isbn) != 13:
            raise forms.ValidationError("ISBN must be exactly 13 characters long.")
        return isbn


class LibraryForm(forms.ModelForm):
    """Form for creating and editing libraries"""
    
    class Meta:
        model = Library
        fields = ['name', 'location', 'books']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter library name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter library location'
            }),
            'books': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['books'].queryset = Book.objects.all()
        self.fields['books'].required = False


class BookReviewForm(forms.ModelForm):
    """Form for creating and editing book reviews"""
    
    class Meta:
        model = BookReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your review here...'
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

