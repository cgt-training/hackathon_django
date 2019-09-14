from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import warnings; warnings.simplefilter('ignore')
import os
import json
from django.conf import settings
import requests
import numpy as np
import csv
import ast

from datetime import *


try:
	special_days = open(os.path.join(settings.BASE_DIR, 'datasets/special_days.csv'))
	movie_day = pd.read_csv(special_days)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

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


# Create your views here.
def movieDay(request):
	
	movie_day_var = movie_day
	moviedetailVar = moviedetail
	
	datem = datetime.now().strftime('%m') +'-' +datetime.now().strftime('%d')

	date_var = movie_day_var[movie_day_var['date'].str.contains(str(datem))==True].to_dict('records')
	
	#print(date_var)
	mov_details= ''
	tag_value = ""
	#if 0 in date_var:
	#if 'keywords' in date_var[]:
	for keywords in date_var:
		tag_value = date_var[0]['keywords']

		if tag_value:
			tag_data = moviedetailVar[moviedetailVar['overview'].str.contains(tag_value)==True].head(1)
			movie_id = int(tag_data.id)
			mov_details = getMovieDetailMovieDay(movie_id)
			#print(type(mov_details))
			json_data = mov_details['genres']
			#json_data = ast.literal_eval(genresStr)
			
			#genres1 = json_data#json.dumps(json_data)
			genres = ""
			for genre in json_data:
				genres = genres + genre['name'] + ' | '

			mov_details['genres'] = genres

	myData ={
		"moviedetail": mov_details
	}
		
	# date_var = movie_day_var[movie_day_var['date'].str.contains(str(datem))==True].head(1).values
	
	# print(date_var)
	# tag_value = date_var[0][2]
	
	# mov_details= ''
	
	# tag_data = moviedetailVar[moviedetailVar['overview'].str.contains(tag_value)==True].head(1)

	# movie_id = int(tag_data.id)

	# mov_details = getMovieDetailMovieDay(movie_id)
	
	# print(type(mov_details))	  
	# myData ={
	# 	"moviedetail": mov_details
	# }

	return render(request,"movieoftheday/movieOfTheDay.html", myData)


def getMovieDetailMovieDay(movies_links_tmdbId):
	response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(movies_links_tmdbId))
	response_movie_detail = response.json()
	# print(response_movie_detail)
	return response_movie_detail

