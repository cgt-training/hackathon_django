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


def dummy(request):

	if 'id' in request.session:
		del request.session['id']
	if 'firstCall' in request.session:
		del request.session['firstCall']
	if 'user_genre' in request.session:
		del request.session['user_genre']
	if 'sim_movie' in request.session:
		del request.session['sim_movie']
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

	smd_Adventure = smd[smd['genres'].str.contains('Adventure')]

	smd_Animation = smd[smd['genres'].str.contains('Animation')]

	smd_Children = smd[smd['genres'].str.contains('Children')]

	smd_Comedy = smd[smd['genres'].str.contains('Comedy')]

	smd_Crime = smd[smd['genres'].str.contains('Crime')]

	smd_Drama = smd[smd['genres'].str.contains('Drama')]

	smd_Fantasy = smd[smd['genres'].str.contains('Fantasy')]

	smd_FilmNoir = smd[smd['genres'].str.contains('Film-Noir')]

	smd_Horror = smd[smd['genres'].str.contains('Horror')]

	smd_IMAX = smd[smd['genres'].str.contains('IMAX')]

	smd_Musical = smd[smd['genres'].str.contains('Musical')]

	smd_Mystery = smd[smd['genres'].str.contains('Mystery')]

	smd_Romance = smd[smd['genres'].str.contains('Romance')]

	smd_SciFi = smd[smd['genres'].str.contains('Sci-Fi')]

	smd_Thriller = smd[smd['genres'].str.contains('Thriller')]

	smd_War = smd[smd['genres'].str.contains('War')]

	smd_Western = smd[smd['genres'].str.contains('Western')]

	mean_Action = smd_Action['vote_average'].mean()
	mean_Adventure = smd_Adventure['vote_average'].mean()
	mean_Animation = smd_Animation['vote_average'].mean()
	mean_Children = smd_Children['vote_average'].mean()
	mean_Comedy = smd_Comedy['vote_average'].mean()
	mean_Crime = smd_Crime['vote_average'].mean()
	mean_Drama = smd_Drama['vote_average'].mean()
	mean_Fantasy = smd_Fantasy['vote_average'].mean()
	mean_FilmNoir = smd_FilmNoir['vote_average'].mean()
	mean_Horror = smd_Horror['vote_average'].mean()
	mean_IMAX = smd_IMAX['vote_average'].mean()
	mean_Musical = smd_Musical['vote_average'].mean()
	mean_Mystery = smd_Mystery['vote_average'].mean()
	mean_Romance = smd_Romance['vote_average'].mean()
	mean_SciFi = smd_SciFi['vote_average'].mean()
	mean_Thriller = smd_Thriller['vote_average'].mean()
	mean_War = smd_War['vote_average'].mean()
	mean_Western = smd_Western['vote_average'].mean()

	array_meanObj = [
		{'smd_Action': smd_Action, 'mean': mean_Action},
		{'smd_Adventure': smd_Adventure, 'mean': mean_Adventure},
		{'smd_Animation': smd_Animation, 'mean': mean_Animation},
		{'smd_Children': smd_Children, 'mean': mean_Children},
		{'smd_Comedy': smd_Comedy, 'mean': mean_Comedy},
		{'smd_Crime': smd_Crime, 'mean': mean_Crime},
		{'smd_Drama': smd_Drama, 'mean': mean_Drama},
		{'smd_Fantasy': smd_Fantasy, 'mean': mean_Fantasy},
		{'smd_FilmNoir': smd_FilmNoir, 'mean': mean_FilmNoir},
		{'smd_Horror': smd_Horror, 'mean': mean_Horror},
		{'smd_IMAX': smd_IMAX, 'mean': mean_IMAX},
		{'smd_Musical': smd_Musical, 'mean': mean_Musical},
		{'smd_Mystery': smd_Mystery, 'mean': mean_Mystery},
		{'smd_Romance': smd_Romance, 'mean': mean_Romance},
		{'smd_SciFi': smd_SciFi, 'mean': mean_SciFi},
		{'smd_Thriller': smd_Thriller, 'mean': mean_Thriller},
		{'smd_War': smd_War, 'mean': mean_War},
		{'smd_Western': smd_Western, 'mean': mean_Western}
	]

	quantile_Action = smd_Action['vote_count'].quantile(0.9)
	quantile_Adventure = smd_Adventure['vote_count'].quantile(0.9)
	quantile_Animation = smd_Animation['vote_count'].quantile(0.9)
	quantile_Children = smd_Children['vote_count'].quantile(0.9)
	quantile_Comedy = smd_Comedy['vote_count'].quantile(0.9)
	quantile_Crime = smd_Crime['vote_count'].quantile(0.9)
	quantile_Drama = smd_Drama['vote_count'].quantile(0.9)
	quantile_Fantasy = smd_Fantasy['vote_count'].quantile(0.9)
	quantile_FilmNoir = smd_FilmNoir['vote_count'].quantile(0.9)
	quantile_Horror = smd_Horror['vote_count'].quantile(0.9)
	quantile_IMAX = smd_IMAX['vote_count'].quantile(0.9)
	quantile_Musical = smd_Musical['vote_count'].quantile(0.9)
	quantile_Mystery = smd_Mystery['vote_count'].quantile(0.9)
	quantile_Romance = smd_Romance['vote_count'].quantile(0.9)
	quantile_SciFi = smd_SciFi['vote_count'].quantile(0.9)
	quantile_Thriller = smd_Thriller['vote_count'].quantile(0.9)
	quantile_War = smd_War['vote_count'].quantile(0.9)
	quantile_Western = smd_Western['vote_count'].quantile(0.9)


	array_meanObj = [
		{'smd_Action': smd_Action, 'mean': mean_Action, 'quantile':quantile_Action},
		{'smd_Adventure': smd_Adventure, 'mean': mean_Adventure, 'quantile':quantile_Adventure},
		{'smd_Animation': smd_Animation, 'mean': mean_Animation, 'quantile':quantile_Animation},
		{'smd_Children': smd_Children, 'mean': mean_Children, 'quantile':quantile_Children},
		{'smd_Comedy': smd_Comedy, 'mean': mean_Comedy, 'quantile':quantile_Comedy},
		{'smd_Crime': smd_Crime, 'mean': mean_Crime, 'quantile':quantile_Crime},
		{'smd_Drama': smd_Drama, 'mean': mean_Drama, 'quantile':quantile_Drama},
		{'smd_Fantasy': smd_Fantasy, 'mean': mean_Fantasy, 'quantile':quantile_Fantasy},
		{'smd_FilmNoir': smd_FilmNoir, 'mean': mean_FilmNoir, 'quantile':quantile_FilmNoir},
		{'smd_Horror': smd_Horror, 'mean': mean_Horror, 'quantile':quantile_Horror},
		{'smd_IMAX': smd_IMAX, 'mean': mean_IMAX, 'quantile':quantile_IMAX},
		{'smd_Musical': smd_Musical, 'mean': mean_Musical, 'quantile':quantile_Musical},
		{'smd_Mystery': smd_Mystery, 'mean': mean_Mystery, 'quantile':quantile_Mystery},
		{'smd_Romance': smd_Romance, 'mean': mean_Romance, 'quantile':quantile_Romance},
		{'smd_SciFi': smd_SciFi, 'mean': mean_SciFi, 'quantile':quantile_SciFi},
		{'smd_Thriller': smd_Thriller, 'mean': mean_Thriller, 'quantile':quantile_Thriller},
		{'smd_War': smd_War, 'mean': mean_War, 'quantile':quantile_War},
		{'smd_Western': smd_Western, 'mean': mean_Western, 'quantile':quantile_Western}
	]


	final_genres_array=[]
	key_array_final = []
	for obj in array_meanObj:
		if obj['mean'] >= 6.0 and obj['quantile'] > 2000.0:
			key_array = []
			for key in obj.keys(): 
				key_array.append(key)
			# print(key_array[0])
			key_array_final.append(key_array[0])
			final_genres_array.append(obj)


	index = 0

	final_movies_with_detail = []

	for obj in final_genres_array:
		# print(key_array_final[index])
		keyName = key_array_final[index]
		df2 = obj[keyName]
		mean = obj['mean']
		quantile = obj['quantile']
		q_movies = df2.copy().loc[df2['vote_count'] >= quantile]
		# print(q_movies.shape)

		# Define a new feature 'score' and calculate its value with `weighted_rating()`
		q_movies['score'] = q_movies.apply(weighted_rating, args=(quantile,mean) ,axis=1) 

		#Sort movies based on score calculated above
		q_movies = q_movies.sort_values('score', ascending=False)

		#Print the top 15 movies
		# print(q_movies.head(20))
		q_movies = q_movies.head(20)
		# print(type(keyName))
		keyName = keyName.replace('smd_', '')
		obj = {
			'genre': keyName,
			'movies': q_movies
		}
		final_movies_with_detail.append(obj)
		index = index+1
		
	# print(final_movies_with_detail['movies'])

	moviesArr = []
	genreArr = []
	lengthArr = []
	num = len(final_movies_with_detail)
	for i in range(num):
		lengthArr.append(i)
	for obj in final_movies_with_detail:
		movieD = obj['movies']
		genreD = obj['genre']
		moviesArr.append(movieD)
		genreArr.append(genreD)
	# print(len(moviesArr))
	print(type(moviesArr[0]))
	
	final_movies_json_arr = []
	
	for i in range(num):

		smd_Action_json = []

		for obj in moviesArr[i].iterrows():

			obj[1]['movieId'] = obj[0]
			jsonVal = obj[1]		
			# print(type(jsonVal))
			smd_Action_json.append(jsonVal)
		final_movies_json_arr.append(smd_Action_json)	


	my_context = {
		'moviesArr': final_movies_json_arr,
		'genre': genreArr,
		'size': lengthArr
	}

	# return HttpResponse("<h1>Hello World homepage()</h1>")
	return render(request,"fetchmovie/dummy.html", my_context)



def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)


def moviesDetail(request):

	movieIdParam = float(request.GET["movieId"])
	tmdbId = int(movieIdParam)
	# print(movieIdParam)
	moviedetailVar = moviedetail

	# genre_li = request.session['user_genre']
	# print('---------TOP Movies--------------------')
	# print(genre_li)
	# links_tmdbId = links.drop(['imdbId'],axis=1)

	metaRow = moviedetailVar.loc[moviedetailVar.id == str(tmdbId)]
	metaRow = metaRow.to_dict('records')

	genresStr = metaRow[0]['genres']
	json_data = ast.literal_eval(genresStr)
	
	#genres1 = json_data#json.dumps(json_data)
	genres = ""
	for genre in json_data:
		genres = genres + genre['name'] + '| '

	my_context ={
		# "movie_list": movie_names_arrays,
		"moviedetail": metaRow[0],
		"genres" : genres
	}
		
	return render(request,"fetchmovie/movies_detail.html",my_context)



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










"""
	********************************************************************************************************
								These functions are not used currently.	
	********************************************************************************************************
"""


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
	********************************************************************************************************
										Collab Filtering 
	********************************************************************************************************
"""


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



"""
	********************************************************************************************************
							Movie of the day functions	
	********************************************************************************************************
"""


def movieDay(request):
	# session_id = 0
	# if 'id' in request.session:
	# 	session_id = request.session['id']

	movie_day_var = movie_day
	moviedetailVar = moviedetail
	#movie_day
	# today = datetime.today()

	# my_date = "2019-09-11"

	datem = datetime.now().strftime('%m') +'-' +datetime.now().strftime('%d')

	date_var = movie_day_var[movie_day_var['date'].str.contains(str(datem))==True].head(1).values
	
	print(date_var)
	tag_value = date_var[0][2]
	
	mov_details= ''
	
	tag_data = moviedetailVar[moviedetailVar['overview'].str.contains(tag_value)==True].head(1)

	movie_id = int(tag_data.id)

	mov_details = getMovieDetailMovieDay(movie_id)
	
	print(type(mov_details))	  
	myData ={
		"moviedetail": mov_details
	}

	return render(request,"fetchmovie/movieOfTheDay.html", myData)


def getMovieDetailMovieDay(movies_links_tmdbId):
	response = requests.get('https://api.themoviedb.org/3/movie/%s?api_key=5fd1f6ffb210aadcdec1444aaea3fc4a' %(movies_links_tmdbId))
	response_movie_detail = response.json()
	# print(response_movie_detail)
	return response_movie_detail