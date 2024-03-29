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
	if 'firstCall' not in request.session:
		user_genre_li = getUserSpecificGenre(request, request.session['id'])
		request.session['user_genre'] = user_genre_li
	if 'id' in request.session:
		session_id = request.session['id']

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
		"user_genre_list": user_genre_li
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
		# print(e)
		print('')

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


def top_movies(request):

	genre_li = request.session['user_genre']
	print('---------TOP Movies--------------------')
	print(genre_li)
	# links_tmdbId = links.drop(['imdbId'],axis=1)
	
	return render(request,"fetchmovie/top_movies.html",{})

def dummy(request):

	if 'id' in request.session:
		del request.session['id']
	if 'firstCall' in request.session:
		del request.session['firstCall']
	if 'user_genre' in request.session:
		del request.session['user_genre']
	
	moviesVar = movies 

	moviedetailVar = moviedetail

	links_small = links

	moviesVar = pd.merge(moviesVar,links_small).drop(['title','imdbId'],axis=1)
	
	links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
	
	moviedetailVar = moviedetailVar.drop([19730, 29503, 35587])
	

	moviedetailVar['id'] = moviedetailVar['id'].astype('int')
	smd = moviedetailVar[moviedetailVar['id'].isin(links_small)]
	smd = smd.drop(['genres'],axis=1)

	smd = moviesVar.merge(smd, left_on='tmdbId', right_on='id')

	smd['genres'] = smd['genres'].fillna('')

	smd_Action = smd[smd['genres'].str.contains('Action')]

	smd_Comedy = smd[smd['genres'].str.contains('Comedy')]

	smd_Horror = smd[smd['genres'].str.contains('Horror')]

	# smd_
	# print(smd_Action['vote_average'])
	# print(smd_Comedy['vote_average'])
	# print(smd_Horror['vote_average'])

	smd_Action = smd_Action.query('vote_average >= 6.5 & vote_count >= 1500')

	smd_Comedy = smd_Comedy.query('vote_average >= 6.5 & vote_count >= 1500')

	smd_Horror = smd_Horror.query('vote_average >= 6.5 & vote_count >= 1500')

	# smd_Action = smd_Action.nlargest(20)
	smd_Action.sort_values('vote_average', inplace=True, ascending=False)

	smd_Comedy.sort_values('vote_average', inplace=True, ascending=False)

	smd_Horror.sort_values('vote_average', inplace=True, ascending=False)

	smd_Action = smd_Action.head(20)

	smd_Comedy = smd_Comedy.head(20)

	smd_Horror = smd_Horror.head(20)

	smd_Action_json = []

	for obj in smd_Action.iterrows():

		obj[1]['movieId'] = obj[0]
		jsonVal = obj[1]		
		# print(type(jsonVal))
		smd_Action_json.append(jsonVal)

	# print(smd_Action_json)
	
	smd_Comedy_json = []	

	for obj in smd_Comedy.iterrows():
				
		obj[1]['movieId'] = obj[0]
		jsonVal = obj[1]		
		# print(type(jsonVal))
		smd_Comedy_json.append(jsonVal)

	smd_Horror_json =[]

	for obj in smd_Comedy.iterrows():
				
		obj[1]['movieId'] = obj[0]
		jsonVal = obj[1]		
		# print(type(jsonVal))
		smd_Horror_json.append(jsonVal)	
		

	my_context ={
		"action_movie_list": smd_Action_json,
		"comedy_movie_list": smd_Comedy_json,
		"horror_movie_list":smd_Horror_json
	}

	# return HttpResponse("<h1>Hello World homepage()</h1>")
	return render(request,"fetchmovie/dummy.html", my_context)

 

def dummy_old(request):

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
		movie_response = getMovieDetail1(movies_links_tmdbId)
		# movie_response = 'Testing'
		response_movie_detail.append(movie_response)
		# print(movie_response)
	
	my_context ={
		"action_movie_list": response_movie_detail
	}
	return render(request,"fetchmovie/dummy.html", my_context)


def getMovieDetail1(movies_links_tmdbId):
	response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(movies_links_tmdbId))
	response_movie_detail = response.json()
	# print(response_movie_detail)
	return response_movie_detail

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
		# data = json.loads(my_json)
		# print(type(data))
		# json_data = json.dumps(data, indent=4, sort_keys=True)
		# print(data['adult'])
		# print('- ' * 20)
		# print(s)

		return HttpResponse(my_json)






"""
	Following functions will fetch data from a specific movie and will store it in a csv file. to find out the 
	details of each movie.
"""


def getMoviesDetail(request):
	linksVar = links
	# print(linksVar)
	tmdbId = getTMDBID(linksVar)
	
	response_movies_objects = []
	i = 0
	for tmdb in tmdbId:
		movieObjects = getMovieDetail1(tmdb)
		response_movies_objects.append(movieObjects)
		# print(response_movies_objects)
		i = i +1
		if i >20:
			break
	print(type(response_movies_objects[0]))
	writeDictToCSV(response_movies_objects)
	return HttpResponse("<h1>Hello World getMoviesDetail()</h1>")

def getTMDBID(linksVar):
	try:
		links_tmdbId = linksVar.drop(['movieId','imdbId'],axis=1)
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
		# print(len(tmdbId_array))
		return tmdbId_array
	except Exception as e:
		print(e)
		return -1


def writeDictToCSV(movie_objects):
	# file_movies_detail
	keys = movie_objects[0].keys()
	with file_movies_detail as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(movie_objects)
