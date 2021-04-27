from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import re
import math
import operator
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

content_wt=0.25
title_wt=0.75

def champion_list(data_index):
    for word,tp in data_index.items():
        posting_list = tp[0]
        posting_list.sort(key=operator.itemgetter(1),reverse=True)
        data_index[word] = (posting_list[0:100],tp[1])   


#Updates the main index using the temporary index created for document.
def update_index(temp_index,data_index,doc_id):
	for word,tf in temp_index.items():
		wordTuple = data_index.get(word,([],0))
		post = wordTuple[0]
		post.append((doc_id, (tf[1]*title_wt+tf[0]*content_wt)))
		data_index[word] = (post,wordTuple[1]+1)


def update_temp_index(word,temp_index,flag):
    arr_tuple = temp_index.get(word,(0,0))
    arr = list(arr_tuple)  #since tuples immutable so converting to list
    if flag==1:
        arr[0] = arr[0] + 1 #0 gives content count 1 gives title count
    elif flag==2:
        arr[1] = arr[1] + 1
    temp_index[word] = arr

#Reads a document and updates the index.
def add_doc_to_index(text, title, doc_id, data_index):
    temp_index = {}
    # for line in text.splitlines():
    text = text.replace('-', ' ') #splitting - words (decide whether to split or not)
    title= title.replace('-', ' ')
    for word in nltk.word_tokenize(text):
        # for word in line.strip().split(" "):
        word = word.lower()        #Converting word to lower case.
    #If word only has alphabet characters, update index.
        if word.isalpha():
            update_temp_index(word,temp_index,1)
	#If word has non-alphabet characters, remove them first.
        else:
            extract_word = []
            for c in word:
                if c.isalpha():
                    extract_word.append(c)
            if len(extract_word)>0:
                str1=''
                extract_word= str1.join(extract_word)
                update_temp_index(extract_word,temp_index,1)
    for word in nltk.word_tokenize(title):
        # for word in line.strip().split(" "):
        word = word.lower()        #Converting word to lower case.
    #If word only has alphabet characters, update index.
        if word.isalpha():
            update_temp_index(word,temp_index,2)
	#If word has non-alphabet characters, remove them first.
        else:
            extract_word = []
            for c in word:
                if c.isalpha():
                    extract_word.append(c)
            if len(extract_word)>0:
                str1=''
                extract_word= str1.join(extract_word)
                update_temp_index(extract_word,temp_index,2)
    # print(temp_index)
    update_index(temp_index,data_index,doc_id)


def update_temp_doc_index(word,doc_id,temp_doc_index):
    temp_doc_index[word] = temp_doc_index.get(word,0)+1

def open_file(file_name):  
    # print("hello")
    f = open(os.path.join(os.path.dirname(__file__),
             os.pardir, file_name), encoding="utf8")
    data = f.read()
    return data


def read_file(file_name, data_index):
    # print("hello")
    global id_title_index
    data = open_file(file_name=file_name)
    docs = BeautifulSoup(data, "html.parser")
    for doc in docs.find_all('doc'):
        id = doc["id"]
        title = doc["title"]
        text = doc.get_text()
        id_title_index[id] = title
        # add_title_to_index(title,id,data_index)
        add_doc_to_index(text, title,id, data_index)


data_index = {}
id_title_index = {}

read_file("wiki_37", data_index)
# read_file("wiki_64", data_index)
champion_list(data_index)
doc_count = len(id_title_index)
data_file = open("index", "wb")
pickle.dump(data_index, data_file)
data_file.close()

index_file = open("index", "rb")
primIndex = pickle.load(index_file)
index_file.close()

output_file = open("readable_content_index.txt","w")
print("\nContent index saved in readable format in 'readable_content_index.txt'.")
for key,val in primIndex.items():
	output_file.write("\n\n"+key+":")
	output_file.write("\n\tDF = "+str(val[1]))
	output_file.write("\n\tPosting List: "+str(val[0]))
output_file.close()
