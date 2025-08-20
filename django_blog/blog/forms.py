from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Post
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment…'
            })
        }
        labels = {
            'content': 'Comment'
        }


    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Comment cannot be empty.')
        if len(content) < 3:
            raise forms.ValidationError('Comment must be at least 3 characters long.')
        return content

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ("username", "email")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "image")

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
