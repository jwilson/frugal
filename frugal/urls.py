# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin

from .views import HomeView, LoginView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LoginView.as_view(), name='logout'),

    url(r'^', include('money.urls', namespace='money')),

    url(r'^$', HomeView.as_view(), name='home')
]
