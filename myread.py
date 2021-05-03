from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import nltk
import numpy as np
from nltk.tokenize import word_tokenize     
import re

combined_docs = []

def normalize_word(word,temp_index):
    word = re.sub('[\W_]+', '', word.lower())
    if len(word)>1:
        update_doc_index(word,temp_index)
#function to dump varibles using pickle
def pickle_file(filename,variable):
    fileopen = open(filename, 'wb')
    pickle.dump(variable,fileopen)
    fileopen.close()

def read_file(filename,all_docs):
    for i in [37]:
        f = open(filename, encoding="utf8")
        filecontent = f.read()
        # Separating the different documents using a split on end doc tag
        docs = filecontent.split("</doc>")
        # Parsing the split output docs using bs and lxml leaving the last split as it would be empty
        docs = [BeautifulSoup(doc + "</doc>", "lxml") for doc in docs][:-1]
        combined_docs.extend(docs)
        f.close()

read_file("wiki_37",combined_docs)
read_file("wiki_64",combined_docs)
#print("length of docs  " + len(combined_docs))

def add_doc_to_index(doc_id,doc_title,doc_text,docs_dict,all_docs):
    for doc in combined_docs:
        id = doc.find_all("doc")[0].get("id")
        title = doc.find_all("doc")[0].get("title")
        text = doc.get_text()
        doc_id.append(id)
        doc_title.append(title)
        doc_text.append(text)
        docs_dict[id] = title

def normalize(doc_id,tokens,weight,square_weight,tdf,doc_text):
    for i in range(len(doc_id)):
        docid = doc_id[i]
        #print(docid)
        tokens = nltk.word_tokenize(doc_text[i])
        for word in tokens:
            if word in tdf:
                if docid in tdf[word]:
                    tdf[word][docid] = tdf[word][docid]+1
                    weight[word][docid] = 1 + np.log(tdf[word][docid])
                else:
                    tdf[word][docid] = 1
                    weight[word][docid] = 1
    #Calculating weight according to logarithmic scheme
    for i in range(len(doc_id)):
        docid = doc_id[i]
        #print(docid)
        tokens = nltk.word_tokenize(doc_text[i])
        squaredoc = 0
        for word in tokens:
            squaredoc = squaredoc + weight[word][docid]**2
        for word in tokens:
            normd[word][docid] = (weight[word][docid] / np.sqrt(squaredoc))


#     for word in tdf:
#         for docid in tdf[word]:
#             square_weight[word] = square_weight[word] + weight[word][docid]**2

# #    print(normd[word][docid])
# #Normalizing weight
#     for word in tdf:
#         square = (np.sqrt(square_weight[word]))
#         for docid in tdf[word]:
#             normd[word][docid] = (weight[word][docid] / square)
    #print(len(normd))
    #Calculating idf value of terms
    for word in vocabulary:
        if(len(normd[word])==0):
            idf[word] = 0
        else:
            idf[word] = np.log10(len(doc_id)/len(weight[word]))
            print(word)
            print(idf[word])



doc_id = [] 
doc_title = [] 
doc_text = [] 
docs_dict = {} 

add_doc_to_index(doc_id,doc_title,doc_text,docs_dict,combined_docs)

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

normalize(doc_id,tokens,weight,square_weight,tdf,doc_text);
#print(len(doc_id))    

pickle_file('vocabularyfile',vocabulary)
pickle_file('tdffile',tdf)
pickle_file('weightfile',weight)
pickle_file('normfile',normd)
pickle_file('idfile',idf)
pickle_file('docdict',docs_dict)
pickle_file('doc_text',doc_text)
