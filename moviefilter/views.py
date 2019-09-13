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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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


def filterOnGenre(request):

	genreParam = request.GET["genre"]
	user_genre_li = request.session['user_genre']
	all_genre = request.session['all_genre']
	session_id = 0
	if 'id' in request.session:
		session_id = request.session['id']
	
	# print(genreParam)
	smd = filterCSVOnGenre(request, genreParam)
	
	print(smd.empty)

	if smd.empty:
		mycontext ={
			'final_movie_data':[],
			'user_genre_li': user_genre_li,
			'remaining_genre': all_genre		
		}

		return render(request,"moviefilter/specificgenre.html",mycontext)

	smd_small_movieId =  smd['movieId']

	smd_data = UserMoviesWithRating(request, smd_small_movieId, smd, session_id)
	
	top_rated_movie_by_user = smd_data['top_rated_movie_by_user']
	user_movies_to_remove = smd_data['user_movies_to_remove']

	smd = removeMoviesUserWatched(request, smd, user_movies_to_remove)

	# print('&&&&&&&&&&----------&&&&&&&&&&----------')
	
	features = ['cast', 'crew', 'keywords']
	
	for feature in features:
	    smd[feature] = smd[feature].apply(literal_eval)
	# print(smd.shape)

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
	for movieN in top_rated_movie_by_user:
		similar_movies = get_recommendations(movieN, cosine_sim2, indices, smd) 
		similar_movies_Array.append(similar_movies.values)

	# print(similar_movies_Array)

	smd = smd.set_index('title')

	final_movie_data = getMovieDetailWithName(similar_movies_Array, smd)    

	# print(final_movie_data[25].name)
	# print(user_genre_li)	

	mycontext ={
		'final_movie_data':final_movie_data,
		'user_genre_li': user_genre_li,
		'remaining_genre': all_genre,
		'genreParam': genreParam
	}

	return render(request,"moviefilter/specificgenre.html",mycontext)
	# return HttpResponse('<h1> From filterOnGenre Function</h1>')

def removeMoviesUserWatched(request, smd, user_movies_to_remove):
	# print('&&&&&&&&&&--removeMoviesUserWatched()--&&&&&&&&&&----------')
	# print(user_movies_to_remove)
	smd = smd.reset_index()
	smd = smd[~smd['movieId'].isin(user_movies_to_remove)]
	return smd

def filterCSVOnGenre(reques, genreParam):

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

	genre_str = genreParam
	smd = smd[smd['genres'].str.contains('%s'%(genre_str))]

	# print('&&&&&&&&&&--filterCSVOnGenre()--&&&&&&&&&&----------')
	# print(smd)
	return smd
	# print(type(small_keywordCSV['id'][0]))
	#Output the shape of tfidf_matrix
	# print(smd.shape)

	
def UserMoviesWithRating(request, smd_small_movieId, smd, session_id):
	# print('&&&&&&&&&&--UserMoviesWithRating()--&&&&&&&&&&----------')
	user_cond = session_id
	
	user_cond = int(user_cond)
	# print(type(user_cond))
	rating_cond = 0.5

	ratingsVar = ratings

	ratingsVar['movieId'] = ratingsVar['movieId'].astype('int')
	small_ratings = ratingsVar[ratingsVar['movieId'].isin(smd_small_movieId)]


	user_rating = small_ratings[small_ratings['userId']==user_cond][['rating','movieId']]
	user_rating = user_rating[user_rating.sort_values(by=['rating'],ascending=False)['rating'] >= rating_cond]
	# print(ratings.shape)
	# print(small_ratings.shape)

	top_user_movies_rating = user_rating.sort_values('rating', ascending=False)

	user_movies_to_remove = top_user_movies_rating['movieId']

	# print(user_movies_to_remove)

	user_movies_to_remove = user_movies_to_remove.iloc[3:]

	# print(user_movies_to_remove)

	top_user_movies_rating = top_user_movies_rating.head(3)
	# print(top_user_movies_rating)
	# moviesVar = moviesVar.set_index('movieId')
	user_favroite_movie_id = []
	for m_id in top_user_movies_rating['movieId']:
		user_favroite_movie_id.append(m_id)

	# print(user_favroite_movie_id)

	#  user_favroite_movie_id will be use to fetch movie details from smd dataframe

	smd = smd.set_index('movieId')

	top_rated_movie_by_user = []

	for m_id in user_favroite_movie_id:
		movieName = smd.loc[m_id]
		top_rated_movie_by_user.append(movieName.title)

	# print(top_rated_movie_by_user)
	myObj = {
		'top_rated_movie_by_user':top_rated_movie_by_user,
		'user_movies_to_remove': user_movies_to_remove
	}
	return myObj

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
	print('--------------&&&&&&&&&&&-----------')
	print(idx)
	arr =[]
	print(type(idx) != np.int64)  #== int64
	if type(idx) != np.int64:
		arr = idx.values
		idx = arr[0]
	# if idx == pd.Series():
	# 	print(idx.values())
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