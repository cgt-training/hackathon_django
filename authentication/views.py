from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import warnings; warnings.simplefilter('ignore')
import os
import json
from django.conf import settings
from django.shortcuts import render
import requests
import numpy as np
import csv
# Create your views here.

try:
	file_ratings = open(os.path.join(settings.BASE_DIR, 'datasets/ratings.csv'))
	ratings = pd.read_csv(file_ratings)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')
try:
	file_movies = open(os.path.join(settings.BASE_DIR, 'datasets/movies.csv'))
	movies = pd.read_csv(file_movies)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_links = open(os.path.join(settings.BASE_DIR, 'datasets/links.csv'))
	links = pd.read_csv(file_links)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_movies_detail = open(os.path.join(settings.BASE_DIR, 'datasets/movies_metadata.csv'))
	moviedetail = pd.read_csv(file_movies_detail)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')



def index(request):
	print('Login')
	if request.method == "POST":
		username = request.POST['login']
		print('**********-----------------*********')
		print(username)
		request.session['id'] = username
	# 	template = loader.get_template('my_template.html')
	# 	context = {"message": "any message"}
	# 	return HttpResponse(template.render(context, request))
		return HttpResponse('<h1> From Login Function</h1>')






	