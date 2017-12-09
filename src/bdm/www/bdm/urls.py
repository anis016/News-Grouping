from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stock-news/', views.stock, name='stock'),
    url(r'^detail', views.detail, name='detail'),
    #url(r'^about/', views.about, name='about'),
    #url(r'^contact/', views.contact, name='contact'),
    #url(r'^detail/(?P<objId>[a-f\d]{24})/$', views.detail, name='detail'),
]