from django.urls import path

from . import views

urlpatterns = [
	path('', views.moviesDetail, name='moviesDetail'),
    # path('recommended', views.index, name='index'),
]


