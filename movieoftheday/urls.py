from django.urls import path

from . import views

urlpatterns = [
	path('', views.movieDay, name='movieDay'),
    # path('recommended', views.index, name='index'),
]