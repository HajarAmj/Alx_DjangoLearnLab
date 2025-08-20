from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Post, Tag
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

class PostForm(forms.ModelForm):
    # free text field for tags (comma separated)
    tags = forms.CharField(
        required=False,
        help_text='Comma-separated tags (e.g. django, python, tutorial)',
        widget=forms.TextInput(attrs={'placeholder': 'django, python'})
    )

    class Meta:
        model = Post
        # include fields you use for creating/editing posts
        fields = ['title', 'content', 'tags']  # add other fields if needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prefill tags for existing instance
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = ', '.join([t.name for t in self.instance.tags.all()])

    def _clean_tag_names(self, tags_str):
        return [t.strip() for t in tags_str.split(',') if t.strip()]

    def save(self, commit=True):
        # Save Post instance first
        instance = super().save(commit=False)
        if commit:
            instance.save()

        tags_str = self.cleaned_data.get('tags', '')
        tag_names = self._clean_tag_names(tags_str)

        # Build Tag objects (case-insensitive dedup)
        new_tags = []
        for name in tag_names:
            # find by case-insensitive match first
            tag = Tag.objects.filter(name__iexact=name).first()
            if not tag:
                tag = Tag.objects.create(name=name)
            new_tags.append(tag)

        # set M2M
        if commit:
            instance.tags.set(new_tags)
            self.save_m2m()
        else:
            # If not committing, attach tags later (rare)
            self._pending_tags = new_tags

        return instance
