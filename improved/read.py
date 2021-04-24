from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import re



def add_to_primary_index(temp_doc_index,doc_id,data_index,isTitle):
    print(1)
    for word,term_frequency in temp_doc_index.items():
        wordMap = data_index.get(word,)
        innermap = word[0]
       # if(isTitle):


def update_temp_doc_index(word,doc_id,temp_doc_index):
    temp_doc_index[word] = temp_doc_index.get(word,0)+1

def add_title_to_index(title, doc_id, data_index):
    
    temp_doc_index = {}
    for word in title.strip().split(" "):
        word = re.sub('[\W_]+', '', word.lower())
        update_temp_doc_index(word,doc_id,temp_doc_index)
    add_to_primary_index(temp_doc_index,doc_id,data_index,True)

def open_file(file_name):
    print("hello")
    f = open(os.path.join(os.path.dirname(__file__),
             os.pardir, file_name), encoding="utf8")
    data = f.read()
    return data


def read_file(file_name, data_index):
    print("hello")
    global id_title_index
    data = open_file(file_name=file_name)
    docs = BeautifulSoup(data, "lxml")
    for doc in docs.find_all('doc'):
        id = doc["id"]
        title = doc["title"]
        text = doc.get_text()
        id_title_index[id] = title
        add_title_to_index(title,id,data_index)
        add_doc_to_index(text, id, data_index)


data_index = {}
id_title_index = {}

read_file("wiki_37", data_index)
read_file("wiki_64", data_index)

doc_count = len(id_title_index)

data_file = open("data_index", "wb")
pickle.dump(data_index, data_file)
data_file.close()

id_title_file = open("id_index", "wb")
pickle.dump(id_title_index, id_title_file)
id_title_file.close()

print(str(doc_count) +
      " docs were parsed and stored in the index of size"+str(len(data_index)))
