from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.utils import timezone
from django.core.urlresolvers import reverse
from embed_video.fields import EmbedVideoField
from django.core.files import File
import os, urllib

class PostQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='posts/', blank=True)
    movie = EmbedVideoField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)

    objects = PostQuerySet.as_manager()
    tags = TaggableManager(blank=True)

    def save(self, *args, **kwargs):
        if self.image_url:
            result = urllib.request.urlretrieve(self.image_url)
            self.image_url = ''
            self.image.save(
                os.path.basename(self.image_url),
                File(open(result[0], 'rb'))
            )
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save()

    def get_absolute_url(self):
        return reverse('post_detail',
                       args=[self.id, self.slug])

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    avatar = models.ImageField(upload_to='user/avatar/',)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comment')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comment')
    active = models.BooleanField(default=True)