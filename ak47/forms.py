from django import forms
from .models import Post, Profile, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    rem = forms.BooleanField(required=False)


class UserRegistrationForm(UserCreationForm):
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)


class CommentForm(forms.ModelForm):
    class Meta:
       model = Comment
       fields = ('body', )

class UrlImgForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','image_url', 'tags')

    def __init__(self, *args, **kwargs):
        super(UrlImgForm, self).__init__(*args, **kwargs)
        self.fields['image_url'].required = True


    def clean_image_url(self):
        VALID_IMAGE_EXTENSIONS = [
            "jpg",
            "jpeg",
            "png",
            "gif",
        ]
        cd = self.cleaned_data
        extension = cd['image_url'].rsplit('.', 1)[1].lower()
        if extension not in VALID_IMAGE_EXTENSIONS:
            raise forms.ValidationError('Wrong url.')
        return cd['image_url']

class MovieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MovieForm, self).__init__(*args, **kwargs)
        self.fields['movie'].required = True

    class Meta:
        model = Post
        fields = ('title','movie', 'tags')

class ImgForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','image', 'tags')

    def __init__(self, *args, **kwargs):
        super(ImgForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = True

class TagForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('tags',)