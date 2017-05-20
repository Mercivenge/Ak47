from django.contrib import admin
from .models import Post, Comment, Profile

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created', 'author', 'active', 'image', 'movie')
    list_filter = ('active', 'created', 'author')
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, PostAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('avatar', 'user')

admin.site.register(Profile, ProfileAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','post')
    list_filter = ('active', 'created', 'post')
    search_fields = ('post', 'user', 'body')

admin.site.register(Comment, CommentAdmin)
# Register your models here.
