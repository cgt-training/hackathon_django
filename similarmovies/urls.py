from django.urls import path

from . import views

urlpatterns = [
	path('', views.simMovies, name='simMovies'),
    # path('recommended', views.index, name='index'),
]


