from django.urls import path

from . import views

urlpatterns = [
	path('', views.advance_search, name='advance_search'),
	path('search_movie', views.search_movie, name='search_movie'),
    # path('recommended', views.index, name='index'),
]


