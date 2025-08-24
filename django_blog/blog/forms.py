from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post
from taggit.forms import TagWidget


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
        fields = ["title", "content", "tags"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5}),
            "tags": TagWidget(),
        }

