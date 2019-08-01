#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import os
import pandas as pd 
import re
from pandas import Series, DataFrame
from textblob import TextBlob, Word
import nltk
import re
nltk.download('stopwords') 
from nltk.corpus import stopwords 
import string
from nltk.probability import FreqDist
import gensim
from gensim import models # For TF-IDF, LDA
import swifter # Makes applying to datframe as fast as vectorizing
import numpy as np

# Visualization
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

# LDA Visualization
import pyLDAvis
import pyLDAvis.gensim 


# In[37]:


# ------------------- FUNCTIONS ---------------------------------------------------------

# Pre-procesing function

stop_words = stopwords.words('english')
stop_words.extend(['chars', 'char']) # Add from blacklist
stop_words.extend(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
# stop_words.extend(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])
stop_words.extend(['get', 'say', 'gmt', 'dont', 'make', 'want', 'also', 
                   'take', 'since', 'tell', 'like', 'could', 'would', 
                   'should', 'jsfjsdgetelementsbytagnames0p', 'functiondsidvar']) # Adding from LDA topics 

def preprocess_text(doc):
    
    """
    pre-processing using textblob: 
    tokenizing, converting to lower-case, and lemmatization based on POS tagging, 
    removing stop-words, and retaining tokens greater than length 2
    """

    blob = TextBlob(doc)
    result = []
    tag_dict = {"J": 'a', # Adjective
                "N": 'n', # Noun
                "V": 'v', # Verb
                "R": 'r'} #  Adverb

    for sent in blob.sentences:

        words_and_tags = [(w, tag_dict.get(pos[0])) for w, pos in sent.tags]    
        lemmatized_list = [w.lemmatize(tag) for w, tag in words_and_tags]
#         stemmed_list = [w.stem() for w in sent.word]

        for token in lemmatized_list:
            if token.lower() not in stop_words and len(token.lower()) > 2:
                result.append(token.lower())

#     print(" ".join(result))
#     print(" ")
    return result



# Function for word frequencies

def get_frequency(processed_text_list): 

    """
    An NLTK function
    Gets frequency distribution of all words in a tokenized list
    We also sort these frequencies in descending order
    """

    word_frequency = FreqDist(word for word in processed_text_list)

    sorted_counts = sorted(word_frequency.items(), key = lambda x: x[1], reverse = True)

    return sorted_counts


def save_file_tokens(processed_docs, retained_vocabulary):
    
    result = []
    
    for token in processed_docs:
        if token in retained_vocabulary:
            result.append(token)

#     print(" ".join(result))
#     print(" ")
    return result


def short_filter_after_preprocess(processed_tokens):
    
    result = []
    
    for token in processed_tokens:
        if token in short_retained_vocabulary:
            result.append(token)
        
    return result


def long_filter_after_preprocess(processed_tokens):
    
    result = []
    
    for token in processed_tokens:
        if token in long_retained_vocabulary:
            result.append(token)
        
    return result


# ----------------------------------------------------------------------------------------


# In[ ]:


# directory = "C:/Users/Shreya/Desktop/Threat_detective/all un news/"

# for files in glob.glob(directory + '*.csv'):

#     print(files[53:]) #23


# In[ ]:


directory = "C:/Users/Shreya/Desktop/Threat_detective/all un news/Temp/"
print(len(directory))


# In[6]:


print(type(data_url))


# In[39]:



# We shall first import all the CSV files that we have on file
# We store all these files in a list


import pandas as pd
import glob

# directory = "/home/sdbookhu/FullNews/"

directory = "C:/Users/Shreya/Desktop/Threat_detective/all un news/Temp/"
all_articles = glob.glob(directory + "/*.csv")

all_articles_list = []

# Storing to list

for file in all_articles:
    df = pd.read_csv(file, index_col = None, header = 0)
    all_articles_list.append(df)

    
print("The total number of CSV files is: " + str(len(all_articles_list)))  

# Now, we will read in files from the list based on our sliding window

window = (4 - 1) # This is for a sliding window of size 4
    
for i in range(0, (len(all_articles_list) - window)):
    
    data_all = pd.concat(all_articles_list[i:i+window], axis=0, ignore_index=True)
    
    name = 'Apr_1_2019_' + str(i) + '_window_' + str(window+1)
    
    print(name)

    # ------------------- PRE-PROCESS SHORT ARTICLES ---------------------------------------------------------


    data_text = data_all.copy()
    
    
    print("Total number of short articles is: ", len(data_text))
    
    data_text = data_text.dropna(subset = ["content"]) # Not all articles have any content available
    print("Total number of short articles after dropping blank ones: ", len(data_text))
    
    data_text = data_text.drop_duplicates(subset="title", keep = "last") # We have many repeating articles
    print("Total number of unique short articles is: ", len(data_text))
    
    short_remove_special_characters = re.compile('([^\w\s-]|_)+')
    data_text['content'].replace(to_replace= short_remove_special_characters, value='', regex=True, inplace=True)
    

    # ------------------- PRE-PROCESS LONG ARTICLES ---------------------------------------------------------

    # For LONG (full) articles 
  
    print("Total number of long articles left is: ", len(data_text))
    
    data_text = data_text.dropna(subset = ["full-content"]) # Not all articles have any content available
    print("Total number of long articles after dropping blank ones: ", len(data_text))
    
    # Remove hyperlinks from content
    long_link_remove = re.compile(r'http\S+')                             
    data_text['full-content'].replace(to_replace= long_link_remove, value='', regex=True, inplace=True)

    long_remove_let_your_friends_know = re.compile(r'Let friends in your social network know what you are reading about .*? Please read the rules before joining the discussion.')
    data_text['full-content'].replace(to_replace= long_remove_let_your_friends_know, value='', regex=True, inplace=True)

    long_remove_last_for_more_coverage_1 = re.compile(r'___ For more .*? This material may not be published, broadcast, rewritten or redistributed.')
    long_remove_last_for_more_coverage_2 = re.compile(r'___ For more .*? by Automated Insights,  using data from STATS LLC, ')
    long_remove_last_for_more_coverage_3 = re.compile(r'For more AP.*? by Automated Insights,  using data from STATS LLC, ')
    data_text['full-content'].replace(to_replace= long_remove_last_for_more_coverage_1, value='', regex=True, inplace=True)
    data_text['full-content'].replace(to_replace= long_remove_last_for_more_coverage_2, value='', regex=True, inplace=True)
    data_text['full-content'].replace(to_replace= long_remove_last_for_more_coverage_3, value='', regex=True, inplace=True)
    
    short_remove_special_characters = re.compile('([^\w\s-]|_)+')
    data_text['content'].replace(to_replace= short_remove_special_characters, value='', regex=True, inplace=True)
    


    # We will apply preprocessing to the whole dataframe 
    
    # First Short
    
    data_text['short_processed_text'] = data_text['content'].swifter.apply(preprocess_text)
    
#     data_text_index = data_text.reset_index()
    
    # Then Long

    data_text['long_processed_text'] = data_text['full-content'].swifter.apply(preprocess_text)
    
    data_text_index = data_text.reset_index()
    
    """
    To get full "dictionary" -- for word frequencies
    """
    
    
    short_all_processed_docs_list = data_text_index.short_processed_text.to_list() # Converts all rows to one big list of lists
    short_all_processed_docs_list = [item for sublist in short_all_processed_docs_list for item in sublist] # List of lists to one simple list

    short_all_docs_frequency = get_frequency(short_all_processed_docs_list) # Using the function written above


    # Vocabulary object:
    # This takes in all unique words from each file of articles and appends to a list
    # We also add these unique words to a text file

    short_all_vocabulary = open("short_all_vocabulary.txt", encoding="utf8").readlines()
    
    short_all_vocabulary = list(set(short_all_vocabulary))

    for word in short_all_docs_frequency:
        if word[0] not in short_all_vocabulary:
            short_all_vocabulary.append(word[0])

    short_all_vocabulary.sort()

    with open('short_all_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in short_all_vocabulary:
            f.write("%s" % word)   


    # NOTE: This includes all the numbers appearing in each article
    
    # Gensim's in-built dictionary

    short_text_dictionary = gensim.corpora.Dictionary(data_text_index.short_processed_text)

    """
    gensim has its own high and low pass filters as shown below.
    However, we are unable to see exactly which words were removed.
    """

    # Include words in dictionary that appear greater than 5 times - Low pass
    # but less than 0.5 proportion of the frequency of all the words in all of the articles - High pass
    print("Total length of short content dictionary before filtering is: ", len(short_text_dictionary))
    short_text_dictionary.filter_extremes(no_below = 5, no_above=0.5) 
    print("Total length of short content dictionary after filtering is: ", len(short_text_dictionary))

    # Blacklist object:
    # This takes in all the "words" that were filtered out and appends to a list
    # We also add these filtered out "words" to a text file
    # We also create a separate object that maintains all "words" not filtered out and create a text file for the same

    short_blacklist = open("short_blacklist.txt", encoding="utf8").readlines()
    short_retained_vocabulary = open("short_retained_vocabulary.txt", encoding="utf8").readlines()
    
    short_blacklist = list(set(short_blacklist))
    short_retained_vocabulary = list(set(short_retained_vocabulary))
    

    for word in short_all_vocabulary:
        if word not in short_text_dictionary.token2id.keys():
            short_blacklist.append(word)
        else:
            short_retained_vocabulary.append(word)

    short_blacklist.sort()
    short_retained_vocabulary.sort()

    with open('short_blacklist.txt', 'a', encoding="utf-8") as f:
        for word in short_blacklist:
            f.write("%s\n" % word)

    with open('short_retained_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in short_retained_vocabulary:
            f.write("%s\n" % word)


    # NOTE: This includes all the numbers appearing in each article

    
    """
    All the words have been mapped to an "ID" using gensim.corpora.Dictionary
    Now, within each individual "document" (news article), we can get the corresponding word counts.
    Unfortunately, gensim only allows for getting document-level word frequencies.
    """
    

#     # TF-IDF depending on the time and filtering window

#     # short_main_corpus = [short_text_dictionary.doc2bow(doc) for doc in short_processed_docs]


#     # # TF-IDF on the bag of words corpus

#     # short_tfidf = models.TfidfModel(short_main_corpus)
#     # short_tfidf_main_corpus = tfidf[short_main_corpus]
    
#     print(" ")
    
    

    long_all_processed_docs_list = data_text_index.long_processed_text.to_list() # Converts all rows to one big list of lists
    long_all_processed_docs_list = [item for sublist in long_all_processed_docs_list for item in sublist] # List of lists to one simple list

    long_all_docs_frequency = get_frequency(long_all_processed_docs_list) 


    # Vocabulary object:
    # This takes in all unique words from each file of articles and appends to a list
    # We also add these unique words to a text file

    long_all_vocabulary = open("long_all_vocabulary.txt", encoding="utf8").readlines()
    
    long_all_vocabulary = list(set(long_all_vocabulary))

    for word in long_all_docs_frequency:
        if word[0] not in long_all_vocabulary:
            long_all_vocabulary.append(word[0])

    long_all_vocabulary.sort()

    with open('long_all_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in long_all_vocabulary:
            f.write("%s\n" % word)   


    # NOTE: This includes all the numbers appearing in each article


    # Gensim's in-built dictionary

    long_text_dictionary = gensim.corpora.Dictionary(data_text_index.long_processed_text)

    """
    gensim has its own high and low pass filters as shown below.
    However, we are unable to see exactly which words were removed.
    """

    # Include words in dictionary that appear greater than 5 times - Low pass
    # but less than 0.5 proportion of the frequency of all the words in all of the articles - High pass
    print("Total length of long content dictionary before filtering is: ", len(long_text_dictionary))
    long_text_dictionary.filter_extremes(no_below = 5, no_above=0.5) 
    print("Total length of long content dictionary after filtering is: ", len(long_text_dictionary))



    # Blacklist object:
    # This takes in all the "words" that were filtered out and appends to a list
    # We also add these filtered out "words" to a text file
    # We also create a separate object that maintains all "words" not filtered out and create a text file for the same

    long_blacklist = open("long_blacklist.txt", encoding="utf8").readlines()
    long_retained_vocabulary = open("long_retained_vocabulary.txt", encoding="utf8").readlines()
    
    long_blacklist = list(set(long_blacklist))
    long_retained_vocabulary = list(set(long_retained_vocabulary))

    for word in long_all_vocabulary:
        if word not in long_text_dictionary.token2id.keys():
            long_blacklist.append(word)
        else:
            long_retained_vocabulary.append(word)

    long_blacklist.sort()
    long_retained_vocabulary.sort()

    with open('long_blacklist.txt', 'a', encoding="utf-8") as f:
        for word in long_blacklist:
            f.write("%s\n" % word)

    with open('long_retained_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in long_retained_vocabulary:
            f.write("%s\n" % word)


    # NOTE: This includes all the numbers appearing in each article


    """
    All the words have been mapped to an "ID" using gensim.corpora.Dictionary
    Now, within each individual "document" (news article), we can get the corresponding word counts.
    Unfortunately, gensim only allows for getting document-level word frequencies.
    """


    # TF-IDF depending on the time and filtering window

    # long_main_corpus = [long_text_dictionary.doc2bow(doc) for doc in long_processed_docs]


    # # TF-IDF on the bag of words corpus

    # long_tfidf = models.TfidfModel(long_main_corpus)
    # long_tfidf_main_corpus = tfidf[long_main_corpus]
    
    
    
    
#     --------------------------------------- SAVING PRE-PROCESSED TEXT TO FILE --------------------
    
    
    
    data_text_index['short_processed_text'] = data_text_index['short_processed_text'].swifter.apply(short_filter_after_preprocess)
    data_text_index['long_processed_text'] = data_text_index['long_processed_text'].swifter.apply(long_filter_after_preprocess)
    
    
    data_url = data_text_index['url']
    data_source = data_text_index['source_name']
    data_publish_time = data_text_index['publishedAt']
    data_title = data_text_index['title']
    data_description = data_text_index['description']
    data_short_content = data_text_index['content']
    data_full_content = data_text_index['full-content']
    data_short_tokens = data_text_index['short_processed_text']
    data_long_tokens = data_text_index['long_processed_text']
    
    
    """
    Use the script below to make changes to the CSV file and save as a different CSV file 
    """

#     save_directory = "/home/shreyac/cleaned_news/"
    save_directory = r'C:/Users/Shreya/Desktop/Threat_detective/all pro news/Temp/'
    
    news_url = []
    news_source = []
    news_publish_time = []
    news_title = []
    news_description = []
    news_short_content = []
    news_full_content = []
    short_processed_tokens = []
    long_processed_tokens = []
    

    for i in range(0, len(data_text_index)):

        news_url.append(data_url[i])
        news_source.append(data_source[i])
        news_publish_time.append(data_publish_time[i])
        news_title.append(data_title[i])
        news_description.append(data_description[i])
        news_short_content.append(data_short_content[i])
        news_full_content.append(data_full_content[i])
        short_processed_tokens.append(data_short_tokens[i])
        long_processed_tokens.append(data_long_tokens[i])


    news_file_df = DataFrame({'url': news_url,
                    'source': news_source,
                    'published_at': news_publish_time,
                    'title': news_title,
                    'description': news_description,
                    'short_content': news_short_content,
                    'full_content': news_full_content,
                    'short_processed_tokens': short_processed_tokens
                    'long_processed_tokens': long_processed_tokens})

    news_file_df = news_file_df[['url', 'source', 'published_at', 'title',
                                     'description', 'short_content', 'short_processed_tokens'
    , 'full_content']]

    save_path = save_directory + name + '.csv'
    
    news_file_df.to_csv(save_path, index = None, header=True, encoding='utf-8')

    
# #     ------------------------------------- LDA ---------------------------------------------
    
#     short_main_corpus = [short_text_dictionary.doc2bow(doc) for doc in short_processed_docs.short_processed_text]

#     short_lda_model = gensim.models.ldamodel.LdaModel(short_main_corpus, 
#                                            num_topics = 20, 
#                                            id2word = short_text_dictionary, 
#                                            random_state = 0,
#                                            chunksize = 1000,
#                                            passes = 20,
#                                            alpha ='auto',
#                                            per_word_topics = True)

#     """
    
#     Add string to demarcate sliding window
    
#     """

#     # # SAVING THE MODEL:

#     # short_lda_model.save('short_lda_model'+'_Apr_15')

#     # # later on, load trained model from file
#     # short_lda_model_load =  models.LdaModel.load('short_lda_model'+'_Apr_15')

#     # # print all topics
#     # short_lda_model_load.show_topics(topics=200, topn=20)

#     # # print topic 28
#     # short_lda_model_load.print_topic(109, topn=20)
    
    
#     # ------------------------ LONG LDA ---------------------------------

#     long_main_corpus = [long_text_dictionary.doc2bow(doc) for doc in long_processed_docs.long_processed_text]

#     long_lda_model = gensim.models.ldamodel.LdaModel(long_main_corpus, 
#                                            num_topics = 20, 
#                                            id2word = long_text_dictionary, 
#                                            random_state = 0,
#                                            chunksize = 1000,
#                                            passes = 20,
#                                            alpha ='auto',
#                                            per_word_topics = True)
    
#     """
    
#     Add string to demarcate sliding window
    
#     """
    
#     # # SAVING THE MODEL:

#     # long_lda_model.save('long_lda_model'+'_Apr_15')

#     # # later on, load trained model from file
#     # long_lda_model_load =  models.LdaModel.load('long_lda_model'+'_Apr_15')

#     # # print all topics
#     # long_lda_model_load.show_topics(topics=200, topn=20)

#     # # print topic 28
#     # long_lda_model_load.print_topic(109, topn=20)


    
    
    


# In[ ]:





# In[ ]:





# In[ ]:




