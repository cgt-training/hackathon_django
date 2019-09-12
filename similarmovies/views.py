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



def simMovies(request):

	movieParam = 'Iron Man'
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

	return render(request,"moviefilter/specificgenre.html",mycontext)
	# return HttpResponse('<h1> From filterOnGenre Function</h1>')

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