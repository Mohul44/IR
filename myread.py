from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import nltk
import numpy as np
from nltk.tokenize import word_tokenize     

INDEX = "./pickles/"

def normalize_word(word,temp_index):
	word = re.sub('[\W_]+', '', word.lower())
	if len(word)>1:
		update_doc_index(word,temp_index)

all_docs = []

for i in [37]:
    f = open("M:\IRassignment\Ranked-Retrieval-main\Ranked-Retrieval-main\myfolder\wiki_" + str(i), encoding="utf8")
    docs = f.read().split("</doc>")
    docs = [BeautifulSoup(doc + "</doc>", "lxml") for doc in docs][:-1]
    all_docs.extend(docs)
    f.close()

print(all_docs)


doc_id = []
doc_title = []
doc_text = []
docs_dict = {}

for doc in all_docs:
    id = doc.find_all("doc")[0].get("id")
    title = doc.find_all("doc")[0].get("title")
    text = doc.get_text()
    doc_id.append(id)
    doc_title.append(title)
    doc_text.append(text)
    docs_dict[id] = title

#print(doc_text)


tokens = []
tdf = {}
weight = {}
sos = {}
square_weight = {}
normd = {}
idf = {}

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

for i in range(len(doc_id)):
    docid = doc_id[i]
    tokens = nltk.word_tokenize(doc_text[i])
    for word in tokens:
        if word in tdf:
            if docid in tdf[word]:
                tdf[word][docid] = tdf[word][docid]+1
                weight[word][docid] = 1 + np.log(tdf[word][docid])
                square_weight[word] = square_weight[word] + weight[word][docid]
                square = (np.sqrt(square_weight[word]))
                normd[word][docid] = (weight[word][docid] / square)
                idf[word] = np.log10(len(all_docs) / len(normd[word]))
            else:
                tdf[word][docid] = 1
                idf[word] = 0
            
        
            
