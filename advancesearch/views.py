from django.http import HttpResponse
from django.shortcuts import render

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
# for mood ganpat code
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity



try:
	special_days = open(os.path.join(settings.BASE_DIR, 'datasets/special_days.csv'), errors='ignore')
	movie_day = pd.read_csv(special_days)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_ratings = open(os.path.join(settings.BASE_DIR, 'datasets/ratings.csv'), errors='ignore')
	ratings = pd.read_csv(file_ratings)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')
try:
	file_movies = open(os.path.join(settings.BASE_DIR, 'datasets/movies.csv'), errors='ignore')
	movies = pd.read_csv(file_movies)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_links = open(os.path.join(settings.BASE_DIR, 'datasets/links.csv'), errors='ignore')
	links = pd.read_csv(file_links)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_movies_detail = open(os.path.join(settings.BASE_DIR, 'datasets/movies_metadata.csv'), errors='ignore')
	moviedetail = pd.read_csv(file_movies_detail)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')



def search_movie(request):
	term = request.GET['term']
	# df = pd.read_csv('datasets/movies.csv')
	df = movies
	response_data = df.loc[df.title.str.contains(pat=term, case=False), "movieId":"title"]
	response_data = response_data.head(100)
	#print(response_data)
	response_data = response_data.to_dict('records')
	#response_data = [{'title':'shimba','movieId':'1'},{'title':'maruti','movieId':'2'}]
	return HttpResponse(json.dumps(response_data), content_type="application/json")


def advance_search(request):

	searchText = ""
	genre = ""
	year = ""
	language = ""
	rating = ""

	if 'searchText' in request.GET:
		searchText = request.GET['searchText']

	if 'genre' in request.GET:
		genre = request.GET['genre']

	if 'year' in request.GET:
		year = request.GET['year']

	if 'language' in request.GET:
		language = request.GET['language']

	if 'rating' in request.GET:
		rating = request.GET['rating']

	# DFMovie = pd.read_csv('datasets/movies.csv')
	DFMovie = movies
	# DFLink = pd.read_csv('datasets/links.csv')
	DFLink = links
	# DFMeta = pd.read_csv('datasets/movies_metadata.csv')
	DFMeta = moviedetail

	DFMeta = DFMeta.drop(["belongs_to_collection", "homepage", "runtime", "video", "adult", "budget", "revenue", "spoken_languages", "status", "vote_count"], axis=1)

	joinedMovie = pd.merge(DFMovie, DFLink, on='movieId', how='left')
	joinedMovie = joinedMovie.dropna()
	joinedMovie['tmdbId']=joinedMovie['tmdbId'].astype(int)
	joinedMovie['tmdbId']=joinedMovie['tmdbId'].astype(str)
	movieDataSet = pd.merge(joinedMovie, DFMeta, left_on='tmdbId', right_on='id', how='left')

	movieDataSet[['tagline']] = movieDataSet[['tagline']].fillna('')
	movieDataSet = movieDataSet.dropna()

	movieDataSet['release_date'] = pd.to_datetime(movieDataSet['release_date'])

	if (genre != ""):
		movieDataSet = movieDataSet.loc[movieDataSet.genres_x.str.contains(pat=genre, case=False)]

	#cond1 = movieDataSet.count()

	if (year != ""):
		#movieDataSet = movieDataSet.loc[movieDataSet.release_date.str.contains(pat=year, case=False).notnull()]
		movieDataSet = movieDataSet.loc[movieDataSet.release_date.dt.year == int(year)]

	#cond2 = movieDataSet.count()

	if (language != ""):
		movieDataSet = movieDataSet.loc[movieDataSet.original_language.str.contains(pat=language, case=False)]

	#cond3 = movieDataSet.count()

	if (searchText != ""):
		movieDataSet = movieDataSet[movieDataSet['title_x'].str.contains(searchText) | movieDataSet['original_title'].str.contains(searchText) | movieDataSet['overview'].str.contains(searchText) | movieDataSet['tagline'].str.contains(searchText)] 

	#cond4 = movieDataSet.count()

	if (rating != ""):
		lastRating = float(rating)
		lastRating = lastRating+1.0
		movieDataSet = movieDataSet.loc[(movieDataSet.vote_average >= float(rating)) & (movieDataSet.vote_average < lastRating)]


	#cond5 = movieDataSet.count()

	#count_nan = joinedMovie.isnull().sum(axis = 0)
	#movieDataSetResult = count_nan #movieDataSet.head()
	movieDataSetResult = movieDataSet.head(50)
	movieDataSetResult = movieDataSetResult.to_dict('records')

	resultSet = {
		'result':movieDataSetResult, 
		'searchText' : searchText,
		'genre' : genre,
		'year' : year,
		'language' : language,
		'rating' : rating,
		#'cond1':cond1, 
		#'cond2':cond2, 
		#'cond3':cond3, 
		#'cond4':cond4, 
		#'cond5':cond5
	}

	return render(request, 'advancesearch/advance_search.html', resultSet)

