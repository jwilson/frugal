# coding=utf-8
from django.conf.urls import include, url
from django.contrib import admin

from .views import HomeView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('money.urls', namespace='money')),
    url(r'^$', HomeView.as_view(), name='home')
]
