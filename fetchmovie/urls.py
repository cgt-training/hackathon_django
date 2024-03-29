from django.urls import path

from . import views

urlpatterns = [
	path('', views.dummy, name='dummy'),
    path('recommended', views.index, name='index'),
    path('topmovies', views.top_movies, name='top'),
    path('moviedetail', views.singleMovieRequest, name='moviedetail'),
    path('createdataset', views.getMoviesDetail, name='createdataset'),
        # url(r'^objects/(?P<oid>[0-9]+)/$', views.object_specific_view, name='objects'),

]