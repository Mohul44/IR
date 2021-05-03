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

def preprocess_query(query_text):
    '''
    This function tokenizes the query, converts each word to lower case, 
    removes all punctuations,hyperlinks,special characters, etc. 
    '''
    #remove hyperlinks
    query_text = re.sub(r'http\S+' , "",query_text)
    #convert tab,nextline to single whitespace
    query_text = re.sub('[\n\t]',' ',query_text)    
    #remove whitespace at the ends
    query_text = query_text.strip()
    #remove additional whitespace created from steps above
    query_text = re.sub(' +',' ',query_text)  
    #split the query text
    # query_tokens = re.split(', |_|-|!|?', query_text)
    query_tokens = filter(None, re.split("[, \-!?:_]+", query_text))
    #lowercase 
    query_tokens = [x.lower() for x in query_tokens]
    #only alphanumeric characters allowed in tokens
    alphanumeric = re.compile('[^a-zA-Z0-9]')
    query_tokens = [alphanumeric.sub('', x) for x in query_tokens]
    print(query_tokens)
    return query_tokens
#Function to calculate frequency and lognormal frequency of every term in query and making idf zero of query terms which are not in vocabulary
def build_query_vector(query_freq,vocabulary,query_logfreq,idf):
		for tokens in query_tokens:
			if(tokens in vocabulary):
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

#printing top k documents on basis of lnc.ltc scheme
def display_k_docs(docs_dict,retir_k,sqrt_doc):
	i = 1
	for doc in retir_k:
		doctitlee = docs_dict[doc]
		print(str(i)+"  Document #" + str(doc) + " " + "Title: " + str(doctitlee) + "  score  " + str(float(retir_k[doc])))  
		i = i+1
		if(i>k):break



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

doc_textf = open("doc_text", 'rb')
doc_text = pickle.load(doc_textf)

print(normdfile)

print("please start the test query entering process")
print("Language:English; Preferred format:space separated query,one at a time,try rephrasing if retrieved docs are less than expected")

while True:
    query = ""
    score_d = {}
    for docid in docs_dict:
    	score_d[docid] = 0
    #Input and process query.
   # print("hi")
    #input_and_process_query(query_index)
    query_input  = input("Enter query")
    #print(query_input)

    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    for char in query_input:
    	if char not in punctuations:
    		query = query + char

    #print(query)

    query_tokens = preprocess_query(query)
    #print(query_tokens)
    query_freq = {}
    query_tdfidf = {}
    query_logfreq = {}
    sos_query = 0
    square_val = 0;
    build_query_vector(query_freq,vocabulary,query_logfreq,idf)

    for tokens in query_freq:
    	query_tdfidf[tokens] = query_logfreq[tokens]*idf[tokens]
    	
    for tokens in query_tdfidf:
    	sos_query = sos_query + query_tdfidf[tokens]**2

  
    sos_query_square = np.sqrt(sos_query)

    #Calculating tdf-idf weights of every term.
    for tokens in query_tdfidf:
    	query_tdfidf[tokens] = (query_tdfidf[tokens])/sos_query_square



    #Calculating score of every document on basic of lnc.ltc scheme.
    for tokens in query_tdfidf:
    	if tokens in vocabulary:
    		for doc in tdf[tokens]:
    			score_d[doc] = score_d[doc] + query_tdfidf[tokens]*normd[tokens][doc]

    #Sorting the dictionary and reversing it to have values in descending order.
    sorted_score_d = dict( sorted(score_d.items(), key=operator.itemgetter(1),reverse = True))
    square_doc = 0
    for doc in score_d:
    	square_doc = square_doc + score_d[doc]*score_d[doc]

    sqrt_doc = np.sqrt(square_doc)

    retir_k = sorted_score_d
    display_k_docs(docs_dict,retir_k,sqrt_doc)

    #To break out from the loop/continue.
    ip = input("\nInput 'DONE' to stop, else enter anything else to continue querying\n")
    if ip=='DONE':
        break
print("Exiting test query entering process")      
#end of the process
	












