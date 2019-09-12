from django.urls import path

from . import views

urlpatterns = [
	path('', views.filterOnGenre, name='filterOnGenre'),
    # path('recommended', views.index, name='index'),
]


