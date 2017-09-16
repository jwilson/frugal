# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin

from .views import HomeView, LoginView, LogoutView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    url(r'^', include('money.urls', namespace='money')),

    url(r'^$', HomeView.as_view(), name='home')
]
