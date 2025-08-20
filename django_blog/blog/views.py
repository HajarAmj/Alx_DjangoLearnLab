from django.shortcuts import render, redirect
from .models import Post, Comment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import PostForm

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

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentListView(ListView):
    model = Comment
    template_name = 'blog/comments/comment_list.html'
    context_object_name = 'comments'


    def get_queryset(self):
        self.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return self.post.comments.select_related('author').all()


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['post'] = self.post
        return ctx

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comments/comment_form.html' # not used if posting from detail


    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        form.instance.post = self.post
        form.instance.author = self.request.user
        messages.success(self.request, 'Your comment was posted.')
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})

class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user


    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'You do not have permission to modify this comment.')
            return redirect(comment_parent_detail_url(self.get_object()))
        return super().handle_no_permission()




    def comment_parent_detail_url(comment: Comment):
        return reverse('blog:post_detail', kwargs={'pk': comment.post.pk})

class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comments/comment_form.html'


    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])


    def form_valid(self, form):
        messages.success(self.request, 'Your comment was updated.')
        return super().form_valid(form)


    def get_success_url(self):
        return comment_parent_detail_url(self.get_object())

class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comments/comment_confirm_delete.html'


    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(self.request, 'Your comment was deleted.')
        return super().delete(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})
