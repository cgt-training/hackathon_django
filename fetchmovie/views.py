from django.http import HttpResponse
import pandas as pd
import os
import json
from django.conf import settings
from django.shortcuts import render
import requests
import numpy as np

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


def index(request):
	# ratings = pd.read_csv(file_ratings)
	# movies = pd.read_csv(file_movies)
	ratingsMovies = ratings
	ratingsMovies = pd.merge(movies,ratingsMovies).drop(['genres','timestamp'],axis=1)
	# ratingsMovies_head = ratingsMovies.head(20)
	#print(ratingsMovies)
	user_rating = pd.DataFrame()
	user_rating = ratingsMovies.query('userId == 2')
	#user_rating = ratingsMovies.query('userId == %s' %(user_id))
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
	print(type(sim_movies_out))
	
	df = sim_movies_out.to_frame()
	json_data = df.to_json() 

	y = json.loads(json_data)
	movie_names_keys = y['0'].keys()
	movie_names_arrays = list(movie_names_keys)
	#print(movie_names_arrays)

	#print(type(sim_movies_out))
	my_context ={
		"movie_list": movie_names_arrays,
		"number_movie": 20
	}
	#return HttpResponse("<a href='/movies/dummy'>Hello, world. index.</a>")
	
	return render(request,"fetchmovie/index.html",my_context)

def get_similar(movie_name,rating,corrMatrix):
	try:
		similar_ratings = corrMatrix[movie_name]*(rating-2.5)
		similar_ratings = similar_ratings.sort_values(ascending=False)
		#return HttpResponse("<h1>%s</h1>" % title)
		#print(similar_ratings)
		return similar_ratings
	except Exception as e:
		# return ['continue', -50]
		print(e)

def top_movies(request):
	# ratings = pd.read_csv(file_ratings)
	# movies = pd.read_csv(file_movies)
	# links = pd.read_csv(file_links)
	links_tmdbId = links.drop(['imdbId'],axis=1)
	# links = 0

	top20MoviesArr = top20Movies(ratings,movies,links)
	print(top20MoviesArr)
	
	# return HttpResponse("<h1>Hello World top_Movies</h1>")
	return render(request,"fetchmovie/top_movies.html",{})

def dummy(request):

	ratingsVar = ratings
	moviesVar = movies
	linksVar = links
	
	movies_links = pd.merge(moviesVar,linksVar).drop(['imdbId'],axis=1)
	movies_links_new = pd.DataFrame()
	# movies_links = movies_links.set_index(['title'])
	# movies_links = movies_links.drop(['movieId'],axis=1)
	movies_links_new = movies_links
	# movie_links = movies_links.set_index(['title'],inplace=True)
	movies_links_new = movies_links_new.drop(['movieId'],axis=1)
	movies_links_new.set_index("title",inplace=True)
	
	
	ratingsVar = pd.merge(movies_links,ratingsVar).drop(['timestamp'],axis=1)
	# print(type(movies_links))
	userRatings = ratingsVar.pivot_table(index=['genres'],columns=['title'],values='rating')
	userRatings.head()

	#userRatings = userRatings.fillna(0,axis=1)
	# print(userRatings)
	action_movies = userRatings.loc["Action"]
	action_movies_arr = action_movies.dropna()
	action_movies_arr = action_movies_arr.nlargest(5)
	action_movies_arr_index = action_movies_arr.index
	action_movies_arr_final = action_movies_arr_index.tolist()

	response_movie_detail = []
	i = 0
	for movie_name in action_movies_arr_final:
		movies_links_tmdbId = movies_links_new.loc[movie_name,'tmdbId']
		movie_response = getMovieDetail(movies_links_tmdbId)
		response_movie_detail.append(movie_response)
		# print(movie_response)
	
	# print(response_movie_detail[0])	
	
	# print(action_movies_arr_final)
	
	# To fetch response from the api.

	# for val in tmdbId:
	# 	# print(val)
	# 	response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(val))
	# 	response_movie_detail = response.json()
	# 	tmdbId_array.append(response_movie_detail)
	# 	print(tmdbId_array)
	# 	i = i + 1

	# response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(argID))
	# response_movie_detail = response.json()
	# print(response_movie_detail)
	my_context ={
		"action_movie_list": response_movie_detail
	}
	return render(request,"fetchmovie/dummy.html", my_context)


def getMovieDetail(movies_links_tmdbId):
	response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(movies_links_tmdbId))
	response_movie_detail = response.json()
	# print(response_movie_detail)
	return response_movie_detail

def getTMDBID():
	try:
		links = pd.read_csv(file_links)
		links_tmdbId = links.drop(['movieId','imdbId'],axis=1)
		json_data = links_tmdbId.to_json()
		y = json.loads(json_data)
		json_object = y['tmdbId']
		tmdbId_array = list()
		# print(type(tmdbId_array))
		i=0
		val = 0
		for (k, v) in json_object.items():
			#print("Key: " + k)
			val = v
			tmdbId_array.append(val)
			#print(val)
			i = i+1
		# movie_names_arrays = list(movie_names_keys)
		return tmdbId_array
	except Exception as e:
		print(e)
		return -1

def floatToInt(val):
	value = int(val)
	return value	


def top20Movies(ratings,movies,links):
	ratingsVar = ratings
	moviesVar = movies
	linksVar = links

	ratingsVar = pd.merge(moviesVar,ratingsVar).drop(['timestamp'],axis=1)
	ratingsVar = pd.merge(ratingsVar, linksVar).drop(['imdbId'],axis=1)
	# print(ratingsVar)

	userRatings = ratingsVar.pivot_table(index=['userId'],columns=['title'],values='rating')
	userRatings.head()
	userRatings = userRatings.dropna(thresh=10, axis=1).fillna(0,axis=1)
	userRatings = userRatings.mean(axis=0)
	print(userRatings.loc['Shawshank Redemption, The (1994)'])
	#print(userRatings)
	#print(userRatings.nlargest(20))
	top20MoviesData = userRatings.nlargest(20)
	top20Movies = top20MoviesData.index
	top20MoviesArr = top20Movies.tolist()
	# print(top20MoviesArr)
	return top20MoviesArr

def singleMovieRequest(request):
	data = dict()
	if request.method == "POST":
		movie_obj = request.body
		# print(type(movie_obj))
		my_json = movie_obj.decode('utf8').replace("'", '"')
		print(my_json)
		print('- ' * 20)
		# Load the JSON to a Python list & dump it back out as formatted JSON
		data = json.loads(my_json)
		print(type(data))
		json_data = json.dumps(data, indent=4, sort_keys=True)
		print(data['adult'])
		print('- ' * 20)
		# print(s)

		return HttpResponse(json_data)