from django.urls import path

from . import views

urlpatterns = [
	path('login', views.index, name='index'),
	# path('logout', views.logout, name='logout')   
]