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


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

try:
	file_keywords = open(os.path.join(settings.BASE_DIR, 'datasets/keywords.csv'))
	keywords = pd.read_csv(file_keywords)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')

try:
	file_credits = open(os.path.join(settings.BASE_DIR, 'datasets/credits.csv'))
	credits_csv = pd.read_csv(file_credits)
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

	sim_movies = []
	movieName = ''
	if 'sim_movie' in request.session:
		movieName =  request.session['sim_movie']
		sim_movie = request.session['sim_movie']
		sim_movies = simMovies(request, sim_movie)
		# sim_movies = sim_movies.replace("\'", "\"")
		print(sim_movies)


	# using list comprehension to perform task 
	all_genre = [i for i in all_genre if i not in user_genre_li]	
	# print(all_genre)
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
	# print(movie_detail_array[0].name)

	my_context ={

		"sim_movies": sim_movies,
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
	# print(sorted_genre_count)		

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
	**********************************************************************************************************
										Finding the Similar Movies
	**********************************************************************************************************
"""

def simMovies(request, movie):
	
	# movieParam = 'Iron Man'
	movieParam = movie
	user_genre_li = request.session['user_genre']
	all_genre = request.session['all_genre']
	smd = trainCSV(request)	
	features = ['cast', 'crew', 'keywords']
	
	for feature in features:
	    smd[feature] = smd[feature].apply(literal_eval)
	print(smd.shape)

	# # Define new director, cast, genres and keywords features that are in a suitable form.
	smd['director'] = smd['crew'].apply(get_director)

	# print(smd['director'])

	features = ['cast', 'keywords', 'genres']
	for feature in features:
	    smd[feature] = smd[feature].apply(get_list)

	# print(smd['cast'])	

	# # Apply clean_data function to your features.
	features = ['cast', 'keywords', 'director']

	for feature in features:
	    smd[feature] = smd[feature].apply(clean_data)
	# print(smd['keywords'])
		    
	smd['soup'] = smd.apply(create_soup, axis=1)
	# print(smd['soup'])
	
	# Import CountVectorizer and create the count matrix
	count = CountVectorizer(stop_words='english')
	count_matrix = count.fit_transform(smd['soup'])
	
	# print(count_matrix)
	
	# Compute the Cosine Similarity matrix based on the count_matrix
	cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

	# print(cosine_sim2)
	
	# Reset index of our main DataFrame and construct reverse mapping as before
	smd = smd.reset_index()
	indices = pd.Series(smd.index, index=smd['title'])

	# print(indices)
	
	similar_movies_Array = []
	
	similar_movies = get_recommendations(movieParam, cosine_sim2, indices, smd) 
	similar_movies_Array.append(similar_movies.values)

	# print(similar_movies_Array)

	smd = smd.set_index('title')

	final_movie_data = getMovieDetailWithName(similar_movies_Array, smd)    

	# print(final_movie_data)

	mycontext ={
		'final_movie_data':final_movie_data,
		'user_genre_li': user_genre_li,
		'remaining_genre': all_genre		
	}

	return final_movie_data
	# return render(request,"moviefilter/specificgenre.html",mycontext)
	
def trainCSV(request):

	# print('&&&&&&&&&&--filterCSVOnGenre--&&&&&&&&&&----------')
	ratingsVar = ratings
	
	moviesVar = movies

	md = moviedetail

	keywordCSV = keywords

	links_small = links

	credits = credits_csv

	moviesVar = pd.merge(moviesVar,links_small).drop(['title','imdbId'],axis=1)

	links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
	# print(links_small)
	md = md.drop([19730, 29503, 35587])

	# drop(['timestamp'],axis=1)


	md['id'] = md['id'].astype('int')
	smd = md[md['id'].isin(links_small)]
	smd = smd.drop(['genres'],axis=1)

	credits['id'] = credits['id'].astype('int')
	small_credits = credits[credits['id'].isin(links_small)]

	keywordCSV['id'] = keywordCSV['id'].astype('int')
	small_keywordCSV = keywordCSV[keywordCSV['id'].isin(links_small)]
	# scredits = scredits.drop(['genres'],axis=1)


	smd = moviesVar.merge(smd, left_on='tmdbId', right_on='id')


	smd['genres'] = smd['genres'].fillna('')

	# print(type(smd['id'][0]))

	# print(type(small_credits['id'][0]))

	smd = pd.merge(smd,small_credits)

	# print(smd)

	#Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
	# tfidf = TfidfVectorizer(stop_words='english')

	#Replace NaN with an empty string
	smd['overview'] = smd['overview'].fillna('')

	#Construct the required TF-IDF matrix by fitting and transforming the data
	# tfidf_matrix = tfidf.fit_transform(smd['overview'])

	smd = small_keywordCSV.merge(smd, left_on='id', right_on='id')

	# genre_str = genreParam
	
	print('&&&&&&&&&&--filterCSVOnGenre()--&&&&&&&&&&----------')
	print(smd)
	return smd


# Get the director's name from the crew feature. If director is not listed, return NaN
def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan


# Returns the list top 3 elements or entire list; whichever is more.
def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        #Check if more than 3 elements exist. If yes, return only first three. If no, return entire list.
        if len(names) > 3:
            names = names[:3]
        return names

    #Return empty list in case of missing/malformed data
    return []


def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director']

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(title, cosine_sim, indices, smd):
	# print(str(title))
	idx = indices[title]
	print('----------get_recommendations()&&&&&&&&&&&-----------')
	arr =[]
	print(type(idx) != np.int64)  #== int64
	if type(idx) != np.int64:
		arr = idx.values
		idx = arr[0]

	sim_scores = list(enumerate(cosine_sim[idx]))
	# print(sim_scores)
	sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
	sim_scores = sim_scores[1:11]
	movie_indices = [i[0] for i in sim_scores]
	# Return the top 10 most similar movies
	return smd['title'].iloc[movie_indices]

def getMovieDetailWithName(movieArray, smd):
	final_movie_detail = []
	i = 0
	lengthArr = len(movieArray)
	for i in range(lengthArr):
		for title in movieArray[i]:
			# print(title)
			details = smd.loc[title]
			# print(details)
			final_movie_detail.append(details)  
	return final_movie_detail