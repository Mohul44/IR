from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import nltk
import numpy as np
from nltk.tokenize import word_tokenize     
import re
import operator
import math
import time

k =10 #no. of document to retrieve

def normalize_word(word):
	word = re.sub('[\W_]+', '', word)

normdfile = open("normfile", 'rb')
normd = pickle.load(normdfile)


vocab_file = open('vocabularyfile', 'rb')
vocabulary = pickle.load(vocab_file)

tdfile = open('tdffile', 'rb')
tdf = pickle.load(tdfile)

weightfile = open('weightfile', 'rb')
weight = pickle.load(weightfile)

idfile = open('idfile', 'rb')
idf = pickle.load(idfile)

dmntdictionary = open('docdict', 'rb')
docs_dict = pickle.load(dmntdictionary)

score_d = {}

for docid in docs_dict:
	score_d[docid] = 0

while True:
    query = ""
    #Input and process query.
    print("hi")
    #input_and_process_query(query_index)
    query_input  = input("Enter query")
    print(query_input)

    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    for char in query_input:
    	if char not in punctuations:
    		query = query + char

    print(query)

    query_tokens = word_tokenize(query)
    print(query_tokens)
    query_freq = {}
    query_tdfidf = {}
    query_logfreq = {}
    sos_query = 0

    for tokens in query_tokens:
    	if(tokens in vocabulary):
    		print('inside')
    		if tokens in query_freq:
    			query_freq[tokens] = query_freq[tokens] + 1
    			query_logfreq[tokens] = (1 + np.log10(query_logfreq[tokens]))
    			
    		else:
    			query_freq[tokens] = 1
    			query_logfreq[tokens] = 1 
    	else:
    		query_freq[tokens] = 0
    		query_logfreq[tokens] = 0
    		idf[tokens] = 0

    for tokens in query_freq:
    	query_tdfidf[tokens] = query_logfreq[tokens]*idf[tokens]
    	sos_query = sos_query + query_tdfidf[tokens]**2


  
    sos_query_square = np.sqrt(sos_query)

    for tokens in query_freq:
    	query_tdfidf[tokens] = (query_tdfidf[tokens])/sos_query_square

    for tokens in query_freq:
    	if tokens in vocabulary:
    		for doc in tdf[tokens]:
    			score_d[doc] = score_d[doc] + query_tdfidf[tokens]*normd[tokens][doc]

    sorted_score_d = dict( sorted(score_d.items(), key=operator.itemgetter(1),reverse = True))
    square_doc = 0
    for doc in score_d:
    	square_doc = square_doc + score_d[doc]*score_d[doc]

    sqrt_doc = np.sqrt(square_doc)

    retir_k = sorted_score_d
    i = 1
    for doc in retir_k:
    	doctitlee = docs_dict[doc]
    	print(str(i)+"  Document #" + str(doc) + " " + "Title: " + str(doctitlee) + "  score  " + str(float(retir_k[doc]/sqrt_doc)))  
    	i = i+1
    	if(i>k):break

    #To break out from the loop/continue.
    if input("\nInput E to exit and any other key to enter another query: ").lower()=='e':
        break
	












