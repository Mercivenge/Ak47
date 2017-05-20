from django.conf.urls import url
from . import views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import password_change, password_change_done, password_reset, password_reset_done,\
                                      password_reset_complete, password_reset_confirm
urlpatterns = [
#main url section
url(r'^frontsite$', views.PostListView.as_view(), name='frontsite'),
url(r'^abyss/$', views.AbyssListView.as_view(), name='abyss'),
#url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list,
#    name='post_list_by_tag'),
#url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$',
#    views.post_detail,
#    name='post_detail'),
url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/$', views.PostDetailsView.as_view(), name='post_detail'),
#accounting section
url(r'^login/$', views.LoginView.as_view(), name='login'),
url(r'^ajax/login/$', views.LoginAjaxView.as_view(), name='ajax_login'),
url(r'^logout/$', views.log_out, name='logout'),
url(r'^register/$', CreateView.as_view(template_name='registration/register.html',
                                 form_class=UserCreationForm,
                                 success_url='/login/'), name='register'),
url(r'^ajax/register/$', views.RegisterAjaxView.as_view(), name='ajax_register'),
url(r'^password-change/$', password_change, name='password_change'),
url(r'^password-change/done/$',password_change_done, name='password_change_done'),
url(r'^password-reset/$', password_reset, name='password_reset'),
url(r'^password-reset/done/$', password_reset_done, name='password_reset_done'),
url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
    password_reset_confirm, name='password_reset_confirm'),
url(r'^password-reset/complete/$', password_reset_complete, name='password_reset_complete'),
#add post section
url(r'^add_post/$', views.AddPostView.as_view(), name='add_post'),
url(r'^add_video/$', views.AddMovieView.as_view(), name='add_video'),
url(r'^add_image/$', views.add_image, name='add_image'),
url(r'^url_image/$', views.url_image, name='url_image'),
url(r'^edit_profile/$', views.edit, name='edit_profile'),
url(r'^(?P<tags>[a-zA-Z0-9-]+)/$', views.PostListView, name='taglist'),
]
