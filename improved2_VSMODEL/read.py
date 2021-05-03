from bs4 import BeautifulSoup
import codecs
import pickle
import time
import os.path
import re
import math
import operator
import string
# import nltk

# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')



#Normalizes the index scores.
def normalize(data_index):
    for word,tp in data_index.items():
        posting_list = tp[0]
        df = tp[1]
        #Traversing the posting list.
        for i in range(len(posting_list)):
            doc_id = posting_list[i][0]
            tf = posting_list[i][1]
            #Updating the normalization factor for the document.
            norm[doc_id] = norm.get(doc_id,0) + (tf**2)


#Updates the main index using the temporary index created for document.
def update_index(temp_index,data_index,doc_id):
	for word,tf in temp_index.items():
		wordTuple = data_index.get(word,([],0))
		post = wordTuple[0]
		post.append((doc_id, tf))
		data_index[word] = (post,wordTuple[1]+1)


def update_temp_index(word,temp_index):
    tf = temp_index.get(word,0)
    tf = tf + 1 
    temp_index[word] = tf

#Reads a document and updates the index.
def add_doc_to_index(text, title, doc_id, data_index):
    temp_index = {}
    tokens = preprocess_query(text)
    for token in tokens:
        update_temp_index(token,temp_index)
    update_index(temp_index,data_index,doc_id)

def preprocess_query(text):
    '''
    This function tokenizes the text, converts each word to lower case, 
    removes all punctuations,hyperlinks,special characters, etc. 
    '''
    #remove hyperlinks
    text = re.sub(r'http\S+' , "",text)
    #convert tab,nextline to single whitespace
    text = re.sub('[\n\t]',' ',text)    
    #remove whitespace at the ends
    text = text.strip()
    #remove additional whitespace created from steps above
    text = re.sub(' +',' ',text)  
    #split the query text
    #taking deafult python punctuations and adding space charater in that
    split_delimiter = string.punctuation + ' '
    exp = "[" + split_delimiter + "]+" 
    # query_tokens = filter(None, re.split("[., \-!?:_]+", query_text))
    text_tokens = filter(None, re.split(exp, text))
    #lowercase 
    text_tokens = [x.lower() for x in text_tokens]
    #only alphanumeric characters allowed in tokens
    alphanumeric = re.compile('[^a-zA-Z0-9]')
    text_tokens = [alphanumeric.sub('', x) for x in text_tokens]
    return text_tokens


def open_file(file_name):  
    f = open(os.path.join(os.path.dirname(__file__),
             os.pardir, file_name), encoding="utf8")
    data = f.read()
    return data


def read_file(file_name, data_index):
    global id_title_index
    data = open_file(file_name=file_name)
    docs = BeautifulSoup(data, "html.parser")
    for doc in docs.find_all('doc'):
        id = doc["id"]
        title = doc["title"]
        text = doc.get_text()
        id_title_index[id] = title
        add_doc_to_index(text, title,id, data_index)


start = time.time()  

data_index = {}
norm = {}
id_title_index = {}
read_file("wiki_00",data_index)	#Parsing the first file
read_file("wiki_01",data_index)	#Parsing the second file
read_file("wiki_02",data_index)	#Parsing the third file
normalize(data_index)
# read_file("wiki_64", data_index)

end = time.time()      

doc_count = len(id_title_index)
data_file = open("index", "wb")
pickle.dump(data_index, data_file)
data_file.close()


titleidmap = open("DOCID-title-map", "wb")
pickle.dump(id_title_index, titleidmap)
titleidmap.close()


normmap = open("Norm-map", "wb")
pickle.dump(norm, normmap)
normmap.close()

index_file = open("index", "rb")
primIndex = pickle.load(index_file)
index_file.close()

norm_file = open("Norm-map", "rb")
norm_data = pickle.load(norm_file)
norm_file.close()

output_file = open("readable_content_index_2.txt","w")
print("\nContent index saved in readable format in 'readable_content_index_2.txt'.")
for key,val in primIndex.items():
	output_file.write("\n\n"+key+":")
	output_file.write("\n\tDF = "+str(val[1]))
	output_file.write("\n\tPosting List: "+str(val[0]))
output_file.close()

output_file = open("readable_content_norm_2.txt","w")
for key,val in norm_data.items():
	output_file.write("\n\n"+key+":")
	output_file.write("\n\tNorm constant = "+str(val))
output_file.close()

print("\nNumber of documents parsed = "+str(doc_count))
print("Size of vocabulary = "+str(len(data_index)))
print("Time taken for parsing and indexing = "+str(end-start)+" seconds.\n")