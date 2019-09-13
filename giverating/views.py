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

try:
	file_ratings = open(os.path.join(settings.BASE_DIR, 'datasets/ratings.csv'))
	ratings = pd.read_csv(file_ratings)
except CParserError as e:
	print(e)
	raise formbuilder_core.views.ValidationException('report', 'insufficient')


############ YKB Code ***************

# Rate this movie #

def give_rating(request):
	error = '1' # method not accepted
	if request.method == 'POST' :
		rating = int(request.POST['movieRate'])
		movieid = int(request.POST['movieId'])
		userid = int(request.session['id'])

		if rating != "" and movieid != "" and rating >= 0 and rating <= 5:
			
			import time

			# get id from csv file
			#ratingsCSV = ratings
			ratingsCSV = pd.read_csv("datasets/ratings.csv")

			# now check if already user has give rating to this movie 
			ratingExists = ratingsCSV.loc[(ratingsCSV.userId == userid) & (ratingsCSV.movieId == movieid)]
			#ratingExists = ratingsCSV.loc[(ratingsCSV['userId']==userid) & (ratingsCSV['movieId']==movieid)]
			#print(ratingExists)
			if len(ratingExists.index) :
				error = '2' #'User has already given rating to this movie'
			else : 
				aDataFrame = pd.DataFrame([(userid, movieid, rating, int(time.time()))])
				aDataFrame.to_csv('datasets/ratings.csv', mode='a', index=False, header=False)
				error = '0' #'Rated successfully'
		else :
			error = '3' #'Please give proper rating'

	return HttpResponse(json.dumps({'error': error}), content_type="application/json")