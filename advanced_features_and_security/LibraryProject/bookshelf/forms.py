"""
Secure Django Forms Implementation
This module implements secure forms with comprehensive input validation,
sanitization, and protection against common vulnerabilities.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape, strip_tags
from django.core.validators import RegexValidator
import re
import logging

from .models import Book

# Configure logging
logger = logging.getLogger('django.security')

# ============================================================================
# CUSTOM VALIDATORS FOR SECURITY
# ============================================================================

class SecureTextValidator:
    """
    Custom validator to prevent XSS and other malicious input in text fields.
    """
    
    # Patterns that might indicate XSS attempts
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript URLs
        r'data:text/html',           # Data URLs with HTML
        r'vbscript:',                # VBScript URLs
        r'on\w+\s*=',               # Event handlers (onclick, onload, etc.)
        r'expression\s*\(',          # CSS expressions
        r'@import',                  # CSS imports
        r'<!--.*?-->',               # HTML comments (potential for IE conditional comments)
    ]
    
    def __init__(self, message=None):
        self.message = message or "Input contains potentially dangerous content."
    
    def __call__(self, value):
        """
        Validate that the input doesn't contain potentially dangerous patterns.
        """
        if not isinstance(value, str):
            return
        
        # Check for dangerous patterns (case-insensitive)
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in input: {pattern}")
                raise ValidationError(self.message, code='dangerous_content')
        
        # Check for excessive HTML tags
        stripped = strip_tags(value)
        if len(stripped) < len(value) * 0.7:  # More than 30% HTML tags
            logger.warning("Input with excessive HTML tags detected")
            raise ValidationError("Input contains too much markup.", code='excessive_markup')


def validate_isbn(value):
    """
    Validate ISBN format (ISBN-10 or ISBN-13).
    """
    if not value:
        return  # Empty is allowed
    
    # Remove hyphens and spaces for validation
    isbn = re.sub(r'[\s-]', '', value)
    
    # Check if it's a valid ISBN-10 or ISBN-13 format
    if not (len(isbn) == 10 or len(isbn) == 13):
        raise ValidationError("ISBN must be 10 or 13 digits long.", code='invalid_isbn_length')
    
    # Check if all characters except the last one are digits (last can be 'X' for ISBN-10)
    if len(isbn) == 10:
        if not (isbn[:-1].isdigit() and (isbn[-1].isdigit() or isbn[-1].upper() == 'X')):
            raise ValidationError("Invalid ISBN-10 format.", code='invalid_isbn10')
    else:  # ISBN-13
        if not isbn.isdigit():
            raise ValidationError("Invalid ISBN-13 format.", code='invalid_isbn13')


def validate_publication_year(value):
    """
    Validate publication year is reasonable.
    """
    if value is not None:
        if value < 1000 or value > 2030:
            raise ValidationError(
                "Publication year must be between 1000 and 2030.",
                code='invalid_year'
            )


# ============================================================================
# SECURE FORM CLASSES
# ============================================================================

class BookForm(forms.ModelForm):
    """
    Secure form for creating and editing books.
    
    Security features:
    - Input validation and sanitization
    - XSS prevention
    - Length limitations
    - Pattern validation
    """
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publication_date', 'pages', 'cover', 'language']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 200,
                'placeholder': 'Enter book title',
                'autocomplete': 'off',  # Prevent autocomplete for security
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 100,
                'placeholder': 'Enter author name',
                'autocomplete': 'off',
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 17,  # ISBN-13 with hyphens
                'placeholder': 'Enter ISBN (10 or 13 digits)',
                'pattern': r'[\d\-X]+',  # HTML5 pattern validation
            }),
            'publication_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': '2030-12-31',
                'min': '1000-01-01',
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10000,
                'placeholder': 'Number of pages',
            }),
            'cover': forms.Select(attrs={
                'class': 'form-control',
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 50,
                'placeholder': 'Language (e.g., English, Spanish)',
                'autocomplete': 'off',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add custom validators to fields
        self.fields['title'].validators.append(SecureTextValidator())
        self.fields['author'].validators.append(SecureTextValidator())
        self.fields['isbn'].validators.append(validate_isbn)
        self.fields['language'].validators.append(SecureTextValidator())
        
        # Make certain fields required
        self.fields['title'].required = True
        self.fields['author'].required = True
        
        # Add help text for security awareness
        self.fields['title'].help_text = "Enter the book title (max 200 characters)"
        self.fields['author'].help_text = "Enter the author's name (max 100 characters)"
        self.fields['isbn'].help_text = "Enter valid ISBN-10 or ISBN-13"
    
    def clean_title(self):
        """
        Clean and validate the title field.
        """
        title = self.cleaned_data.get('title')
        
        if not title:
            raise ValidationError("Title is required.", code='required')
        
        # Strip and validate length
        title = title.strip()
        if len(title) < 1:
            raise ValidationError("Title cannot be empty.", code='empty_title')
        
        if len(title) > 200:
            raise ValidationError("Title is too long (max 200 characters).", code='title_too_long')
        
        # Additional security check for SQL injection patterns
        if self._contains_sql_patterns(title):
            logger.warning(f"Potential SQL injection attempt in title: {title[:50]}")
            raise ValidationError("Title contains invalid characters.", code='invalid_characters')
        
        return escape(title.strip())  # HTML escape for XSS prevention
    
    def clean_author(self):
        """
        Clean and validate the author field.
        """
        author = self.cleaned_data.get('author')
        
        if not author:
            raise ValidationError("Author is required.", code='required')
        
        author = author.strip()
        if len(author) < 1:
            raise ValidationError("Author name cannot be empty.", code='empty_author')
        
        if len(author) > 100:
            raise ValidationError("Author name is too long (max 100 characters).", code='author_too_long')
        
        # Check for reasonable author name format
        if not re.match(r'^[a-zA-Z\s\.\-\']+$', author):
            raise ValidationError(
                "Author name contains invalid characters. Only letters, spaces, dots, hyphens, and apostrophes are allowed.",
                code='invalid_author_format'
            )
        
        return escape(author.strip())
    
    def clean_isbn(self):
        """
        Clean and validate the ISBN field.
        """
        isbn = self.cleaned_data.get('isbn')
        
        if not isbn:
            return isbn  # ISBN is optional
        
        isbn = isbn.strip()
        
        # Remove common separators for validation
        clean_isbn = re.sub(r'[\s-]', '', isbn)
        
        # Additional validation beyond the validator
        if len(clean_isbn) not in [
