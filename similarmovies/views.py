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
import ast

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

try:
	file_moods_recommendation = open(os.path.join(settings.BASE_DIR, 'datasets/moods_recommendation.csv'))
	moods_recommendation_csv = pd.read_csv(file_moods_recommendation)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')


def moviesDetail(request):

	# movieIdParam = float(request.GET["movieId"])
	tmdbId = 0
	if 'movieId' in request.GET:
		movieIdParam = float(request.GET["movieId"])
		if movieIdParam :
			tmdbId = int(movieIdParam)

	if 'realMovieId' in request.GET:
		realMovieId = float(request.GET["realMovieId"])
		if realMovieId:
			df = pd.read_csv('datasets/links.csv')
			linkRow = df.loc[df.movieId == realMovieId]
			tmdbId = int(linkRow.tmdbId[linkRow.index[0]])

	# tmdbId = int(movieIdParam)
	# print(movieIdParam)
	moviedetailVar = moviedetail

	moodMovies = moviesOnMood(request, tmdbId)

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
		genres = genres + genre['name'] + ' | '

	sim_movies = metaRow[0]['title']	
	
	request.session['sim_movie'] = sim_movies
	print(request.session['sim_movie'])

		# now add into session for last visited movie name 
	request.session['last_searched_movie'] = str(metaRow[0]['title'])
	request.session.save()

	# language
	spoken_languagesStr = metaRow[0]['spoken_languages']
	json_data = ast.literal_eval(spoken_languagesStr)
	
	spoken_languages = ""
	for lang in json_data:
		spoken_languages = spoken_languages + lang['name'] + ', '


	my_context ={
		# "movie_list": movie_names_arrays,
		"moviedetail": metaRow[0],
		"genres" : genres,
		"spoken_languages" : spoken_languages,
		"moodMovies" : moodMovies
	}

		
	return render(request,"fetchmovie/movies_detail.html",my_context)




def moviesOnMood(request, tmdbId):
	# try:
	# 	file_keywords = open(os.path.join(settings.BASE_DIR, 'datasets/keywords.csv'))
	# 	keywords = pd.read_csv(file_keywords)
	# except CParserError as e:
	# 	print(e)
	# 	raise formbuilder_core.views.ValidationException('report', 'insufficient')

	# kewordsCsv = keywords
	# moodsCsv = moods_recommendation_csv
	moodsCsv = pd.read_csv('datasets/moods_recommendation.csv')
	kewordsCsv = pd.read_csv('datasets/keywords.csv')

	kewordsData = kewordsCsv.loc[kewordsCsv.id == tmdbId]
	#print(kewordsData.head())
	if not kewordsData.empty:
		for index, mood in moodsCsv.iterrows():
			moodVar = str(mood['mood'])
			keyWordExists = kewordsData[kewordsData['keywords'].str.contains(moodVar)] 
			#print(keyWordExists)
			if not keyWordExists.empty:
				# now add to session
				if 'moods' not in request.session:
					request.session['moods'] = {moodVar:1}
					request.session.save()
					#request.session['moods'][moodVar] = 100
				elif moodVar not in request.session['moods']: 
					request.session['moods'][moodVar] = 1
					request.session.save()
				else :
					prevCounter = request.session['moods'][moodVar] + 1
					request.session['moods'][moodVar] = prevCounter
					request.session.save()

	# now check if moods is > 5 
	if 'moods' in request.session:
		for moodCounter in request.session['moods']:
			if int(request.session['moods'][moodCounter]) >= 5:
				findMood = moodsCsv.loc[moodsCsv.mood == moodCounter]
				if not findMood.empty:
					#print(findMood.head())
					findMoodDict = findMood.to_dict('records')
					request.session['mood_set'] = str(findMoodDict[0]['keyword'])
					request.session.save()


	# now check if any mood is set
	moodMovies = ""
	if 'mood_set' in request.session:
		# now ykb pasting ganpat's code here 
		def get_keywords(x):
		    my_keyword = ''
		    for i in x:
		        my_keyword = my_keyword+i['name']+", "
		    my_keyword.rstrip(",")
		    return my_keyword

		def get_recommendations(idx):
		    sim_scores = list(enumerate(cosine_sim[idx]))
		    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
		    sim_scores = sim_scores[1:3]
		    movie_indices = [i[0] for i in sim_scores]
		    return movies.iloc[movie_indices]['title']



		links = pd.read_csv('datasets/links.csv')
		links = links[links['tmdbId'].notnull()]['tmdbId'].astype('int')

		movies = moviedetail
		movies = movies[movies['id'].apply(lambda x : x.isnumeric())]
		movies['id'] = movies['id'].astype('int')

		#Filter to small movies set
		movies = movies[movies['id'].isin(links)]

		keywords2 = kewordsCsv
		keywords2['keywords'] = keywords2['keywords'].apply(literal_eval)
		keywords2['my_keywords'] = keywords2['keywords'].apply(get_keywords)
		keywords2['id'] = keywords2['id'].astype('int')

		movies = movies.merge(keywords2,on='id')

		tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
		tfidf_matrix = tf.fit_transform(movies['my_keywords'])

		cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

		mood = request.session['mood_set']
		movies_with_mood = movies[movies['my_keywords'].str.find(mood)>=0]
		movies_with_mood = movies_with_mood.sort_values(by=['vote_count'],ascending=False)
		movies_with_mood_index = movies_with_mood.index

		#movies_with_mood_index
		mv_idx = []
		mv_recm_idx = []
		for i in movies_with_mood_index:
		    mv_idx.append(i)
		    recm = get_recommendations(i)
		    for j in list(recm.index.values):
		        mv_recm_idx.append(j)

		final_mv_idx = pd.DataFrame(mv_idx+mv_recm_idx,columns=['id'])
		final_data = pd.merge(final_mv_idx,movies,how='left',on='id')
		final_data.drop_duplicates(subset ="id",keep = False, inplace = True)
		final_data = final_data[~final_data['my_keywords'].isnull()]

		#moodMovies = moviedetail
		moodMovies = final_data.head(5)
		moodMovies = moodMovies.to_dict('records')


	return moodMovies
		
	# return render(request,"fetchmovie/movies_detail.html",my_context)





"""
	******************************************************************************************************
									functions below this is not used	
	******************************************************************************************************
"""


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