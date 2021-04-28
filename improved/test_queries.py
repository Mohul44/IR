import re # regex
from collections import Counter
import math 
import pickle
import time # for time taken calcuation
import operator # fro sorting

# Relative weightage given to appearance of a term in title of the document
TITLE_FACTOR = 0.75 
# Relative weightage given to appearance of a body in title of the document
BODY_FACTOR = 0.25 
# Top K documents retrieved for the query
K=10

# No of docs in a champion list
R=100
'''This test query file is build for index of the form 
    {
        'word1':(
                    {
                        'doc1':(tf_equivalent),
                        'doc2':(tf_equivalent),
                        ...
                    },
                    doc_freq_of_word_1
                ),
        'word2':...
    }
    tf_equivalent = cosinenorm (0.75*body_tf + 0.25*title_tf)
    posting list contains top R reverse sorted docs according to
    tf_equivalent
'''


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


def buildqueryvector(query_tokens, index):
    '''
        This function takes tokenized query and index as input, 
        converts into a query vector using LTC weighting scheme
        L = 1+log10(tf)
        T = log10(NO_DOCS/ Doc_freq)
        C= cosine normnalisation
    '''
    #building tf-raw for query
    query_vector = {}
    for token in query_tokens:
        #checking whether token is in vocabulary
        if index.get(token,None) is None:
            print("WARNING: {} is not in vocabulary".format(token))
            continue
        #updating query index
        if token in query_vector:
            query_vector[token] = query_vector.get(token,0) + 1
        else:
            query_vector[token] = 1    

    #building tf-weight*idf for query, calculating q_norm
    q_norm = 0
    for token in query_vector:
        
        tf_weight = 1 + math.log(query_vector[token],10)
        df = (index[token])[1]
        idf = math.log(NO_DOCS/df,10)
        score = tf_weight*idf
        query_vector[token] = score
        q_norm += score * score
    
    q_norm = math.sqrt(q_norm)
    #apply cosine normalisation 
    for token in query_vector:
        query_vector[token] = query_vector[token] / q_norm

    return query_vector    


def score_documents(index, query_vector):
    '''
        takes index and query_vector as an input
        calculate lnc.ltc scores of each document in the champion lists of 
        tokens appearing in query_vector. Assumes query_vector in 
        LTC format as specified in buildqueryvector(). Returns scores 
        sorted in decreasing order 
    '''
    scores={}

    for token in query_vector:

        champion_list = (index[token])[0]

        for entry in champion_list:
            docid = entry[0]
            tf_equivalent = entry[1]
            if docid in scores:
                scores[docid] += query_vector[token] * tf_equivalent
            else:
                scores[docid] = query_vector[token] * tf_equivalent

    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))
    sorted_scores.reverse()
    return sorted_scores


def display_K_docs(sorted_scores):
    '''
        Takes sorted scores of documents wrt to a query 
        in decreasing order and prints top K documents
        if sorted_score has top K documents
    '''

    num_of_docs_retrieved = len(sorted_scores)
    if (num_of_docs_retrieved ==0):
        print("0 Documents retrieved for the given query.Returning to next query\n\n\n")
        return

    if(num_of_docs_retrieved < K):
        print("WARNING: only {} documents retrieved for the given query\n".format(num_of_docs_retrieved))

    no_doc_shown = min(num_of_docs_retrieved, K)

    for count in range(no_doc_shown):
        print("{}. \tid: {} \tscore: {}".format(count+1,sorted_scores[count][0],sorted_scores[count][1]))
        print("\ttitle: {}".format(titleidmap[sorted_scores[count][0]] ))



def readpickle(pkl_filename):
        '''
            reads and returns the pickled index/map; 
            index format is specified in top
        '''  
        pklfile = open(pkl_filename, "rb")
        indexormap = pickle.load(pklfile)
        pklfile.close()
        return indexormap


titleidmap = readpickle("DOCID-title-map")
# No of total documents
NO_DOCS = len(titleidmap)

index = readpickle("index")

print("please start the test query entering process")
print("Language:English; Preferred format:space separated query,one at a time,try rephrasing if retrieved docs are less than expected")


while True:
    query_text = input("\nplease enter query text to be searched in our IR system\n")
    if (len(query_text) ==0):
        print("Empty Query entered, please reenter")
        continue

    start_time = time.time()
    query_token = preprocess_query(query_text)
    query_vector = buildqueryvector(query_token, index)
    sorted_scores = score_documents(index, query_vector)
    end_time = time.time()    
    duration = end_time - start_time
    print("\n{} seconds were taken to execute the query\n".format(duration))

    display_K_docs(sorted_scores)

    # to stop the process
    ip = input("\nInput 'DONE' to stop, else enter anything else to continue querying\n")
    if ip=='DONE':
        break

print("Exiting test query entering process")      
#end of the process

