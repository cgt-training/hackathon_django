from django.urls import path

from . import views

urlpatterns = [
	path('', views.dummy, name='dummy'),
    # path('recommended', views.index, name='index'),
    path('topmovies', views.moviesDetail, name='top'),
    path('moviedetail', views.singleMovieRequest, name='moviedetail'),
    path('createdataset', views.getMoviesDetail, name='createdataset'),
    # path('mvday', views.movieDay, name='mvday'),
    
]


