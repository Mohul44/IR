from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import nltk
import numpy as np
from nltk.tokenize import word_tokenize     
import re

INDEX = "./pickles/"

#For removing non aplha characters and converting the word to lower case
def normalize_word(word,temp_index):
	word = re.sub('[\W_]+', '', word.lower())
	if len(word)>1:
		update_doc_index(word,temp_index)
#function to dump varibles using pickle
def pickle_file(filename,variable):
    fileopen = open(filename, 'wb')
    pickle.dump(variable,fileopen)
    fileopen.close()

all_docs = []
#Opening and combining documents as one using beautiful soup
for i in [37,64]:
    f = open("M:\IRassignment\Ranked-Retrieval-main\Ranked-Retrieval-main\myfolder\wiki_" + str(i), encoding="utf8")
    data = f.read()
    docs = BeautifulSoup(data, "lxml")
    all_docs.extend(docs)
    f.close()

doc_id = []
doc_title = []
doc_text = []
docs_dict = {}

#Adding id, titles, text of every document to doc_id, doc_title, doc_text respectively
for docs in all_docs:
    for doc in docs.find_all('doc'):
        id = doc["id"]
        title = doc["title"]
        text = doc.get_text()
        doc_id.append(id)
        doc_title.append(title)
        doc_text.append(text)
        docs_dict[id] = title

tokens = []
tdf = {}
weight = {}
sos = {}
square_weight = {}
normd = {}
idf = {}

#tokenizing the documents and adding them to vocabulary
for page in doc_text:
    #print(page)
    tokens.extend(nltk.word_tokenize(page))
vocabulary = sorted(set(tokens))


for i in vocabulary:    
    tdf[i] = {}
    weight[i] = {}
    square_weight[i] = 0
    normd[i] = {}
    idf[i] = 0   

#print(len(doc_id))
#calculating term frequency of every token with respect to document
for i in range(len(doc_id)):
    docid = doc_id[i]
    #print(docid)
    tokens = nltk.word_tokenize(doc_text[i])
    for word in tokens:
        if word in tdf:
            if docid in tdf[word]:
                tdf[word][docid] = tdf[word][docid]+1
            else:
                tdf[word][docid] = 1
#Calculating weight according to logarithmic scheme
for word in tdf:
    for docid in tdf[word]:
        weight[word][docid] = 1 + np.log(tdf[word][docid])
        square_weight[word] = square_weight[word] + weight[word][docid]**2
       
#    print(normd[word][docid])
square = (np.sqrt(square_weight[word]))
#Normalizing weight
for word in tdf:
    for docid in tdf[word]:
         normd[word][docid] = (weight[word][docid] / square)

#print(len(normd))
#Calculating idf value of terms
for word in vocabulary:
    if(len(normd[word])==0):
        idf[word] = 0
    else:
        idf[word] = np.log10(len(doc_id)/len(normd[word]))
    

pickle_file('vocabularyfile',vocabulary)
pickle_file('tdffile',tdf)
pickle_file('weightfile',weight)
pickle_file('normfile',normd)
pickle_file('idfile',idf)
pickle_file('docdict',docs_dict)