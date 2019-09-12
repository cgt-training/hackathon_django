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


user_genre_li = []

def index(request):
	
	session_id = 0
	all_genre = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Drama', 'Fantasy', 'FilmNoir', 'Horror', 'IMAX', 'Musical', 'Mystery', 
	'Romance', 'SciFi', 'Thriller', 'War', 'Western']
	if 'firstCall' not in request.session:
		user_genre_li = getUserSpecificGenre(request, request.session['id'])
		request.session['user_genre'] = user_genre_li
	else:
		user_genre_li = request.session['user_genre']
	if 'id' in request.session:
		session_id = request.session['id']

	# using list comprehension to perform task 
	all_genre = [i for i in all_genre if i not in user_genre_li]	
	print(all_genre)
	request.session['all_genre'] = all_genre

	# print(user_genre_li)
	ratingsMovies = ratings
	ratingsMovies = pd.merge(movies,ratingsMovies).drop(['genres','timestamp'],axis=1)
	# ratingsMovies_head = ratingsMovies.head(20)
	#print(ratingsMovies)
	user_rating = pd.DataFrame()
	# user_rating = ratingsMovies.query('userId == 2')
	user_rating = ratingsMovies.query('userId == %s' %(session_id))
	size_user_rating = user_rating.shape
	#print(size_user_rating[0])
	# Creates a list containing 5 lists, each of 8 items, all set to 0
	w, h = 2, size_user_rating[0];
	user_rating_movies = [[0 for x in range(w)] for y in range(h)]
	i=0
	for index, row in user_rating.iterrows():
		user_rating_movies[i][0] = row['title']
		user_rating_movies[i][1] = row['rating']
		i=i+1
		#print(row['title'], row['rating'])
		#print(user_rating_movies)
	user_rating_DF = pd.DataFrame(user_rating)
	#print(user_rating_DF[['title','rating']])
	userRatingsMovies = ratingsMovies.pivot_table(index=['userId'],columns=['title'],values='rating')
	userRatingsMovies.head()

	#print("Before: ",userRatingsMovies.shape)
	#print("Before: ",userRatingsMovies)
	userRatingsMovies = userRatingsMovies.dropna(thresh=10, axis=1).fillna(0,axis=1)
	#userRatingsMovies.fillna(0, inplace=True)
	#print("After: ",userRatingsMovies.shape)
	#print("After: ",userRatingsMovies)
	corrMatrix = userRatingsMovies.corr(method='pearson')
	corrMatrix.head(40)
	romantic_lover = user_rating_movies
	#print(romantic_lover)
	similar_movies = pd.DataFrame()
	for movie,rating in romantic_lover:
		similar_movies = similar_movies.append(get_similar(movie,rating,corrMatrix),ignore_index = False)
		#print(similar_movies)
	#similar_movies.head(10)
	#print(similar_movies)
	sim_movies_out = similar_movies.sum().sort_values(ascending=False).head(20)
	# print(type(sim_movies_out))
	
	df = sim_movies_out.to_frame()
	json_data = df.to_json() 

	y = json.loads(json_data)
	movie_names_keys = y['0'].keys()
	movie_names_arrays = list(movie_names_keys)
	#print(movie_names_arrays)

	"""
		this function will find details of the movie.
	"""
	movie_detail_array = []

	movie_detail_array = getMovieDetail(movie_names_arrays)

	# print('movie_detail_array[0][title]')
	print(movie_detail_array[0].name)

	my_context ={
		# "movie_list": movie_names_arrays,
		"movie_list": movie_detail_array,
		"number_movie": 20,
		"user_genre_list": user_genre_li,
		"remaining_genre": all_genre
	}
	#return HttpResponse("<a href='/movies/dummy'>Hello, world. index.</a>")
	
	return render(request,"fetchmovie/index.html",my_context)


def getMovieDetail(movie_names_arrays):
	links_small = links
	moviesVar = movies
	movies_details = moviedetail


	moviesVar = pd.merge(moviesVar,links_small).drop(['imdbId'],axis=1)

	moviesVar = moviesVar.fillna(0)

	moviesVar['tmdbId'] = moviesVar['tmdbId'].astype('int')

	moviesVar = moviesVar.rename(columns={"tmdbId": "id"})

	links_small_filter = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')

	movies_details = movies_details[movies_details['id'].apply(lambda x : x.isnumeric())]
	movies_details['id'] = movies_details['id'].astype('int')
	movies_details = movies_details.drop(['original_title','title'],axis=1)

	movies_details_filter = movies_details[movies_details['id'].isin(links_small_filter)]
	movies_details_filter = moviesVar.merge(movies_details_filter, left_on='id', right_on='id')

	# print(movies_details_filter.keys())

	movies_details_filter.set_index('title', inplace=True)

	# print(movies_details_filter.keys())
	movie_det_array = []
	# detail = movies_details_filter.loc['Indiana Jones and the Temple of Doom (1984)']
	for movie in movie_names_arrays:
		detail = movies_details_filter.loc[movie]
		movie_det_array.append(detail)

	return movie_det_array
	

def get_similar(movie_name,rating,corrMatrix):
	# print("get_similar()")
	try:
		similar_ratings = corrMatrix[movie_name]*(rating-2.5)
		similar_ratings = similar_ratings.sort_values(ascending=False)
		#return HttpResponse("<h1>%s</h1>" % title)
		#print(similar_ratings)
		return similar_ratings
	except Exception as e:
		# return ['continue', -50]
		print(e)
		

def getUserSpecificGenre(request, userId_P):
	request.session['firstCall'] = 'called'
	ratingsVar = ratings
	moviesVar = movies

	ratingsVar = pd.merge(moviesVar,ratingsVar).drop(['timestamp'],axis=1)

	ratingsVar.head()

	user_rating = pd.DataFrame()

	total_users = 650

	combined_genres_array = []

	# user_rating = ratingsVar.query('userId == 1')
	user_rating = ratingsVar.query('userId == %s' %(userId_P))

	# making boolean series for a team name 
	filter1 = user_rating["rating"]<5.01
	filter2 = user_rating["rating"]>3.99

	filtered_data = user_rating.where(filter1 & filter2, inplace = False).dropna()

	genres_users = filtered_data['genres']

	print('-----------***************-------------')
	final_genres_array = []

	for genre in genres_users:
		value = genre.split('|')
		for word in value:
			if word not in final_genres_array:
				final_genres_array.append(word)

	genres_array = []

	if len(final_genres_array) > 10:
		for word in final_genres_array:
			count = 0
			genre_obj = {'genre':word,'count':0}
			for genre in genres_users:
				present = word in genre
				if present:
					count = count + 1
			genre_obj['count']	= count	
			genres_array.append(genre_obj)

	sorted_genre_count = sorted(genres_array, key = lambda i: i['count'],reverse=True) 
	print(sorted_genre_count)		

	index = 0

	print('-----------***************-------------')

	final_genres_list = []

	for obj in sorted_genre_count:
		genre_value = obj['genre']
		final_genres_list.append(genre_value)
		index = index + 1
		if index > 7:
			break

	# print(final_genres_list)
	return final_genres_list