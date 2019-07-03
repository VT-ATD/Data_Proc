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
from gensim import models # For TF-IDF
import swifter # Makes applying to datframe as fast as vectorizing


# In[2]:


# ------------------- FUNCTIONS ---------------------------------------------------------

# Pre-procesing function

stop_words = stopwords.words('english')
stop_words.extend(['chars', 'char']) # Add from blacklist

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


# ----------------------------------------------------------------------------------------


# In[13]:


# directory = "C:/Users/Shreya/Desktop/Threat_detective/all un news/"

# for files in glob.glob(directory + '*.csv'):

#     print(files[53:]) #23


# In[ ]:





# In[ ]:


# directory = "/home/sdbookhu/FullNews/"

directory = "C:/Users/Shreya/Desktop/Threat_detective/all un news/"

for files in glob.glob(directory+'*.csv'):

    print(files[53:]) #23

#     save_directory = "/home/shreyac/cleaned_news/"

    name = files[53:] # 23

    news_csv_file = pd.read_csv(files)

    data_all = news_csv_file
    data_url = data_all['url']
    data_source = data_all['source_name']
    data_publish_time = data_all['publishedAt']
    data_title = data_all['title']
    data_description = data_all['description']
    data_short_content = data_all['content']
    data_full_content = data_all['full_content']
    
    # data_full_content = data_all['full-content']


    # ------------------- PRE-PROCESS SHORT ARTICLES ---------------------------------------------------------


    short_data_text = data_all[['content', 'title']]
    print("Total number of short articles is: ", len(short_data_text))
    short_data_text = short_data_text.dropna() # Not all articles have "full content" available
    print("Total number of short articles after dropping blank ones: ", len(short_data_text))
    short_data_text = short_data_text.drop_duplicates(subset="title", keep = "last") # We have many repeating articles
    print("Total number of unique short articles is: ", len(short_data_text))
    
    
    
    short_documents = short_data_text[['content']]
    
    short_remove_special_characters = re.compile('([^\w\s-]|_)+')
    short_documents['content'].replace(to_replace= short_remove_special_characters, value='', regex=True, inplace=True)
    
    
    # We will apply preprocessing to the whole dataframe

    short_processed_docs = short_documents['content'].swifter.apply(preprocess_text).to_frame("short_processed_text")
    
    """
    To get full "dictionary" -- for word frequencies
    """

    short_all_processed_docs_list = short_processed_docs.short_processed_text.to_list() # Converts all rows to one big list of lists
    short_all_processed_docs_list = [item for sublist in short_all_processed_docs_list for item in sublist] # List of lists to one simple list

    short_all_docs_frequency = get_frequency(short_all_processed_docs_list) # Using the function written above


    # Vocabulary object:
    # This takes in all unique words from each file of articles and appends to a list
    # We also add these unique words to a text file

    short_all_vocabulary = open("short_all_vocabulary.txt", encoding="utf8").readlines()
    
    short_all_vocabulary = set(short_all_vocabulary)

    for word in short_all_docs_frequency:
        if word[0] not in short_all_vocabulary:
            short_all_vocabulary.append(word[0])

    short_all_vocabulary.sort()

    with open('short_all_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in short_all_vocabulary:
            f.write("%s" % word)   


    # NOTE: This includes all the numbers appearing in each article
    
    # Gensim's in-built dictionary

    short_text_dictionary = gensim.corpora.Dictionary(short_processed_docs.short_processed_text)

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
    
    short_blacklist = set(short_blacklist)
    short_retained_vocabulary = set(short_retained_vocabulary)
    

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


    # TF-IDF depending on the time and filtering window

    # short_main_corpus = [short_text_dictionary.doc2bow(doc) for doc in short_processed_docs]


    # # TF-IDF on the bag of words corpus

    # short_tfidf = models.TfidfModel(short_main_corpus)
    # short_tfidf_main_corpus = tfidf[short_main_corpus]
    
    print(" ")


    # ------------------- PRE-PROCESS LONG ARTICLES ---------------------------------------------------------

    # For LONG (full) articles 

    long_data_text = data_all[['full_content', 'title']]
    print("Total number of long articles is: ", len(long_data_text))
    long_data_text = long_data_text.dropna() # Not all articles have "full content" available
    print("Total number of long articles after dropping blank ones: ", len(long_data_text))
    long_data_text = long_data_text.drop_duplicates(subset="title", keep = "last") # We have many repeating articles
    print("Total number of unique long articles is: ", len(long_data_text))

    long_documents = long_data_text[['full_content']]

    # Remove hyperlinks from content
    long_link_remove = re.compile(r'http\S+')                             
    long_documents['full_content'].replace(to_replace= long_link_remove, value='', regex=True, inplace=True)

    long_remove_let_your_friends_know = re.compile(r'Let friends in your social network know what you are reading about .*? Please read the rules before joining the discussion.')
    long_documents['full_content'].replace(to_replace= long_remove_let_your_friends_know, value='', regex=True, inplace=True)

    long_remove_last_for_more_coverage_1 = re.compile(r'___ For more .*? This material may not be published, broadcast, rewritten or redistributed.')
    long_remove_last_for_more_coverage_2 = re.compile(r'___ For more .*? by Automated Insights,  using data from STATS LLC, ')
    long_remove_last_for_more_coverage_3 = re.compile(r'For more AP.*? by Automated Insights,  using data from STATS LLC, ')
    long_documents['full_content'].replace(to_replace= long_remove_last_for_more_coverage_1, value='', regex=True, inplace=True)
    long_documents['full_content'].replace(to_replace= long_remove_last_for_more_coverage_2, value='', regex=True, inplace=True)
    long_documents['full_content'].replace(to_replace= long_remove_last_for_more_coverage_3, value='', regex=True, inplace=True)


    long_remove_special_characters = re.compile('([^\w\s-]|_)+')
    long_documents['full_content'].replace(to_replace= long_remove_special_characters, value='', regex=True, inplace=True)

    # We will apply preprocessing to the whole dataframe

    long_processed_docs = long_documents['full_content'].swifter.apply(preprocess_text).to_frame("long_processed_text")

    """
    To get full "dictionary" -- for word frequencies
    """

    long_all_processed_docs_list = long_processed_docs.long_processed_text.to_list() # Converts all rows to one big list of lists
    long_all_processed_docs_list = [item for sublist in long_all_processed_docs_list for item in sublist] # List of lists to one simple list

    long_all_docs_frequency = get_frequency(long_all_processed_docs_list) 


    # Vocabulary object:
    # This takes in all unique words from each file of articles and appends to a list
    # We also add these unique words to a text file

    long_all_vocabulary = open("long_all_vocabulary.txt", encoding="utf8").readlines()
    
    long_all_vocabulary = set(long_all_vocabulary)

    for word in long_all_docs_frequency:
        if word[0] not in long_all_vocabulary:
            long_all_vocabulary.append(word[0])

    long_all_vocabulary.sort()

    with open('long_all_vocabulary.txt', 'a', encoding="utf-8") as f:
        for word in long_all_vocabulary:
            f.write("%s\n" % word)   


    # NOTE: This includes all the numbers appearing in each article


    # Gensim's in-built dictionary

    long_text_dictionary = gensim.corpora.Dictionary(long_processed_docs.long_processed_text)

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
    
    long_blacklist = set(long_blacklist)
    long_retained_vocabulary = set(long_retained_vocabulary)

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
    
    
    
    # ------------------------------------------------------------------------------------
    
    print(" ")
    print(name + " done! Next file:")
    
    print(" ")
    print(" ")
    


# In[ ]:





# In[ ]:





# In[ ]:




