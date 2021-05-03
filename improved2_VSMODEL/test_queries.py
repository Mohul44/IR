import re # regex
import math 
import pickle
import time # for time taken calcuation
import operator # fro sorting
import string 


# Top K documents retrieved for the query
K=10
#filter query terms using this idf threshold
MINIDF = 1.3
'''This test query file is build for index of the form 
    {
        'word1':(
                    {
                        'doc1':(tf),
                        'doc2':(tf),
                        ...
                    },
                    doc_freq_of_word_1
                ),
        'word2':...
    }
    posting list contains contains term frequencies of respective 
    documents along with doc freq. 


    A file mapping document title to the document norm 
    value (sum of square of tf-weight is also expected to reduce 
    the computation)    
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
    #taking deafult python punctuations and adding space charater in that
    split_delimiter = string.punctuation + ' '
    exp = "[" + split_delimiter + "]+" 
    # query_tokens = filter(None, re.split("[., \-!?:_]+", query_text))
    query_tokens = filter(None, re.split(exp, query_text))
    #lowercase 
    query_tokens = [x.lower() for x in query_tokens]
    #only alphanumeric characters allowed in tokens
    alphanumeric = re.compile('[^a-zA-Z0-9]')
    query_tokens = [alphanumeric.sub('', x) for x in query_tokens]
    print(query_tokens)
    return query_tokens


def buildqueryvector(query_tokens, index, MINIDF):
    '''
        This function takes tokenized query and index as input, 
        converts into a query vector using LTC weighting scheme
        L = 1+log10(tf)
        T = log10(NO_DOCS/ Doc_freq)
        C= cosine normnalisation

        is terms having idf>MINIDF is less than 3 or all terms have idf > MINIDF, gives normal
        query vector 
        else removes low idf terms and rebuild query vector by recursively calling itself 
    '''
    #building tf-raw for query
    query_vector = {}
    query_idf = {}
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
        query_idf[token] = idf
        score = tf_weight*idf
        query_vector[token] = score
        q_norm += score * score
    
    q_norm = math.sqrt(q_norm)
    #apply cosine normalisation 
    for token in query_vector:
        query_vector[token] = query_vector[token] / q_norm

    val = [True if idf>MINIDF else False for idf in query_idf.values()]
    remaining_terms = sum(val)

    # if terms having desired idf are more than 3
    # then go for removing low idf terms 
    # else do basic vector model
    # if all terms are high idf return the query vector 

    if remaining_terms < 2 or remaining_terms==len(query_idf):
        return query_vector
    # removing low odf terms and calculate query vector again 
    for token in query_idf:
        if query_idf[token] <= MINIDF:
            query_tokens.remove(token)
    return buildqueryvector(query_tokens, index, MINIDF)    

def select_documents(index, query_vector, NO_DOCS_REQD):
    '''
    takes query_vector and index. NO_DOCS_REQD is a parameter stating number of 
    documents to be considered. selects and return NO_DOCS_REQD docs 
    depending upon no of query terms in the documents.  
    '''
    scores_count = {} # count of query terms appearing in document


    for token in query_vector:

        posting_list = (index[token])[0]
        for entry in posting_list:
           # calculate no of query terms appearing in each doc
            docid = entry[0]

            if docid in scores_count:
                scores_count[docid] = scores_count[docid] + 1
            else:
                scores_count[docid] = 1

    #print("count of scores")
    sorted_count_doc = sorted(scores_count.items(), key=operator.itemgetter(1))
    sorted_count_doc.reverse()
    # print(sorted_count_doc)
    
    docs = [x[0] for x in sorted_count_doc]
    # only keep top NO_DOCS_REQD docs reanked by frequency of query terms 
    del docs[NO_DOCS_REQD:]
    return docs


def score_documents(index, query_vector, docnormmap, docs):
    '''
        takes index and query_vector and doc id and norm score map as an input
        calculate lnc.ltc scores of each document in the posting lists of 
        tokens appearing in query_vector. Assumes query_vector in 
        LTC format as specified in buildqueryvector(). Returns scores 
        sorted in decreasing order 

        ONLY documents in docs list are scored 
    '''
    scores={}

    for token in query_vector:

        posting_list = (index[token])[0]

        for entry in posting_list:
            # update score for each doc in champion list 
            docid = entry[0]
            # leave the docid not in docs 
            if docid not in docs:
                continue
            # fetching square of doc norm score 
            docnorm = math.sqrt(docnormmap[docid])
            #normalising tf
            tf_norm = entry[1] / docnorm
            if docid in scores:
                scores[docid] += query_vector[token] * tf_norm
            else:
                scores[docid] = query_vector[token] * tf_norm

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
docnormmap = readpickle("Norm-map")
# No of total documents
NO_DOCS = len(titleidmap)
NO_DOCS_REQD = int(math.sqrt(NO_DOCS))
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
    query_vector = buildqueryvector(query_token, index, MINIDF)
    selected_docs = select_documents(index, query_vector, NO_DOCS_REQD)
    sorted_scores = score_documents(index, query_vector, docnormmap, selected_docs)
    
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
