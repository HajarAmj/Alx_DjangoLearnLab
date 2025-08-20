from django.shortcuts import render, redirect
from .models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm

def post_list(request):
    posts = Post.objects.select_related('author').all()
    return render(request, 'blog/index.html', {'posts': posts})


class UserLoginView(LoginView):
    template_name = 'registration/login.html'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')


    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account was created. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()


    return render(request, 'registration/register.html', {"form": form})




@login_required
def profile(request):
    return render(request, 'profile.html')



@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context = {"u_form": u_form, "p_form": p_form}
    return render(request, 'profile_edit.html', context)
