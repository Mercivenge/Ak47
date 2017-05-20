from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, FormView, UpdateView, TemplateView, CreateView, RedirectView
from django.views.generic.edit import FormMixin
from .models import Profile, Post
from .forms import LoginForm, UserRegistrationForm, CommentForm, ImgForm, MovieForm, UrlImgForm, ProfileEditForm, TagForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from django.conf import settings
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

def post_list(request, tag_slug=None):
    object_list = Post.objects.active()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'ak47/frontsite.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})



class PostListView(ListView, FormMixin):

    queryset = Post.objects.active()
    model = Post
    paginate_by = 10
    template_name = 'ak47/frontsite.html'
    form_class = TagForm
    tag = None

    def get_queryset(self):
        qs = super().get_queryset()
        if 'tag' in self.kwargs:
            tag = self.tag.objects.filtrer(Tag, slug=self.kwargs['tag']).first()
            if tag:
                qs = qs.filter(tags__in=[self.tag])
            else:
                qs = qs.empty()
        return qs

    def get_context_data(self, **kwargs):
        kwargs.update({
            'tag': self.tag
        })
        return super().get_context_data(**kwargs)

class AbyssListView(PostListView):
    queryset = Post.objects.all()

class TagListView(PostListView):
    def get_queryset(self):
        form = self.get_form()
        cd = form.cleaned_data

class PostDetailsView(FormMixin, DetailView):
    model = Post
    template_name = 'ak47/post_detail.html'
    form_class = CommentForm

    def get_queryset(self):
        qs = super().get_queryset().active()
        return qs

    def get_context_data(self, **kwargs):
        context = super(PostDetailsView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['comments'] = obj.comment.filter(active=True)
        context['comment_form'] = self.get_form()
        return context


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            new_comment = form.save(commit=False)
            new_comment.post = self.get_object()
            new_comment.user = user
            new_comment.save()
            return super(PostDetailsView, self).form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk, 'slug': self.object.slug})


def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug, active=True)
    comments = post.comment.filter(active=True)
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = user
            new_comment.save()
    else:
        comment_form = CommentForm
    return render(request,
                  'ak47/post_detail.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form})

class RegisterAjaxView(FormView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
            new_user = form.save(commit=False)
            print(form.data)
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            messages.success(request,'User registered successfully')
            data = {'status': 'ok'}
            return JsonResponse(data=data)

    def form_invalid(self, form):
            data = {'status': 'invalidform'}
            return JsonResponse(data=data)



class RegisterView(FormView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('frontsite')
    template_name = 'registration/register.html'
    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        profile = Profile.objects.create(user=new_user)
        messages.success('User registered successfully')
        return super(RegisterView, self).form_valid(form)

@login_required
def edit(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    if request.method == 'POST':
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'ak47/edit_profile.html', {'profile_form': profile_form})


class LoginView(FormView):
    form_class = LoginForm
    success_url = reverse_lazy('frontsite')
    template_name = 'registration/login.html'
    def form_valid(self, form):
                cd = form.cleaned_data
                user = authenticate(username=cd['username'], password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(self.request, user)
                        if cd['rem']:
                            self.request.session.set_expiry(0)
                        messages.success(self.request, 'Successfully logged in.')
                        return super(LoginView, self).form_valid(form)
                    else:
                        messages.error(self.request, 'This account is banned.')
                else:
                    messages.error(self.request, 'Login and password didn\'t match.')
                return redirect('login')

class LoginAjaxView(FormView):
    form_class = LoginForm
    template_name = 'registration/ajax_login.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if cd['rem']:
                        self.request.session.set_expiry(0)
                    messages.success(request, 'Successfully logged in.')
                    data = {
                        'status':'ok',
                    }
                else:
                    messages.error(request, 'This account is banned.')
                    data = {'status': 'ban'}
            else:
                messages.error(request, 'Invalid combination of username and password')
                data = {'status': 'badlog'}
        else:
            messages.error(request, 'Unable to log in.')
            data = {'status': 'invalidform'}
        return JsonResponse(data)



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if cd['rem']:
                        self.request.session.set_expiry(0)
                    messages.success(request, 'Successfully logged in.')
                    return redirect('frontsite')
                else:
                    messages.error(request, 'This account is banned.')
            else:
                messages.error(request, 'Invalid ')
        else:
            messages.error(request, 'Unable to log in.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def log_out(request):
        logout(request)
        messages.success(request, 'Successfully logged out.')
        return redirect('frontsite')

@login_required
def add_image(request):
    if request.method == 'POST':
        image_form = ImgForm(request.POST, request.FILES)
        if image_form.is_valid():
            user = User.objects.get(username=request.user.username)
            new_post = image_form.save(commit=False)
            new_post.author = user
            new_post.save()
            image_form.save_m2m()
            messages.success(request, 'post successfully added')
            return redirect(new_post)
    else:
        image_form = ImgForm()
    return render(request, 'ak47/img.html', {'image_form': image_form})

@login_required
def add_video(request):
    if request.method == 'POST':
        movie_form = MovieForm(request.POST)
        if movie_form.is_valid():
            user = request.user
            new_post = movie_form.save(commit=False)
            new_post.author = user
            new_post.save()
            movie_form.save_m2m()
            messages.success(request, 'Post successfully added')
            return redirect(new_post)
    else:
        movie_form = MovieForm()
    return render(request, 'ak47/movie.html', {'movie_form': movie_form})

class AddingView(CreateView, LoginRequiredMixin):
        def form_valid(self, form):
            user = self.request.user
            new_post = form.save(commit=False)
            new_post.author = user
            new_post.save()
            form.save_m2m()
            messages.success(self.request, 'Post successfully added')
            return redirect(new_post)
#Problem with weird error.
class AddMovieView(AddingView):
    form_class = MovieForm
    template_name = 'ak47/movie.html'

class AddUrlView(AddingView):
    form_class = UrlImgForm
    template_name = 'ak47/url.html'

class AddImgView(AddingView):
    form_class = ImgForm
    template_name = 'ak47/img.html'

@login_required
def url_image(request):
    if request.method == 'POST':
        url_form = UrlImgForm(request.POST)
        if url_form.is_valid():
            user = User.objects.get(username=request.user.username)
            new_post = url_form.save(commit=False)
            new_post.author = user
            new_post.save()
            url_form.save_m2m()
            messages.success(request, 'Post successfully added')
            return redirect(new_post)
    else:
        url_form = UrlImgForm()
    return render(request, 'ak47/url.html', {'url_form': url_form})

class AddPostView(TemplateView, LoginRequiredMixin):
    template_name = 'ak47/addpost.html'

@login_required
def add_buttons(request):
    return render(request, 'ak47/addpost.html')



