from django.urls import path

from . import views

urlpatterns = [
	path('', views.give_rating, name='give_rating'),
    # path('recommended', views.index, name='index'),
    
]


