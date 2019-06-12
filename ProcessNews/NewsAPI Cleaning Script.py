#!/usr/bin/env python
# coding: utf-8

# In[11]:



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

# directory = "/home/sdbookhu/FullNews/"

directory = "C:/Users/Shreya/Desktop/all un news/"

for files in glob.glob(directory+'*.csv'):

    print(files[35:])

    news_source = []
    news_title = []
    news_description = []
    news_url = []
    news_publish_time = []
    news_content = []
    news_full_content = []

    #      save_directory = "/home/shreyac/cleaned_news/"

    save_directory = "C:/Users/Shreya/Desktop/all pro news/"

    name = files[35:] # 23

    news_csv_file = pd.read_csv(files)

    data_all = news_csv_file
    data_url = data_all['url']
    data_source = data_all['source_name']
    data_publish_time = data_all['publishedAt']
    data_title = data_all['title']
    data_description = data_all['description']
    data_content = data_all['content']
    data_full_content = data_all['full_content']
    
#     data_full_content = data_all['full-content']




"""
Use the script below to make changes to the CSV file and save as a different CSV file 
"""



#     for i in range(0, len(data_all)):

#         news_url.append(data_url[i])
#         news_source.append(data_source[i])
#         news_publish_time.append(data_publish_time[i])
#         news_title.append(data_title[i])
#         news_description.append(data_description[i])
#         news_content.append(data_content[i])
#         news_full_content.append(data_full_content[i])


#     news_file_df = DataFrame({'url': news_url,
#                     'source': news_source,
#                     'published_at': news_publish_time,
#                     'title': news_title,
#                     'description': news_description,
#                     'content': news_content,
#                     'full_content': news_full_content})

#     news_file_df = news_file_df[['url', 'source', 'published_at', 'title',
#                                      'description', 'content', 'full_content']]

# #     save_directory = save_directory + 'enriched_' + name 

#     save_directory = save_directory + name
#     print(save_directory)

#     export_csv = news_file_df.to_csv (save_directory, index = None, header=True)



# ------------------- PRE-PROCESS ---------------------------------------------------------


    data_text = data_all[['full_content', 'title']]
#     print(len(data_text))
    data_text = data_text.dropna() # Not all articles have "full content" available
#     print(len(data_text))
    data_text = data_text.drop_duplicates(subset="title", keep = "last") # We have many repeating articles
#     print(len(data_text))
    
    
    documents = data_text[['full_content']]
    
    # Remove hyperlinks from content
    link_remove = re.compile(r'http\S+')                             
    documents['full_content'].replace(to_replace= link_remove, value='', regex=True, inplace=True)
    
    remove_let_your_friends_know = re.compile(r'Let friends in your social network know what you are reading about .*? Please read the rules before joining the discussion.')
    documents['full_content'].replace(to_replace= remove_let_your_friends_know, value='', regex=True, inplace=True)
    
    remove_last_for_more_coverage_1 = re.compile(r'___ For more .*? This material may not be published, broadcast, rewritten or redistributed.')
    remove_last_for_more_coverage_2 = re.compile(r'___ For more .*? by Automated Insights,  using data from STATS LLC, ')
    remove_last_for_more_coverage_3 = re.compile(r'For more AP.*? by Automated Insights,  using data from STATS LLC, ')
    documents['full_content'].replace(to_replace= remove_last_for_more_coverage_1, value='', regex=True, inplace=True)
    documents['full_content'].replace(to_replace= remove_last_for_more_coverage_2, value='', regex=True, inplace=True)
    documents['full_content'].replace(to_replace= remove_last_for_more_coverage_3, value='', regex=True, inplace=True)

    
    
#     Pre-procesing function

    stop_words = stopwords.words('english')
# stop_words.extend(['know', 'what', 'would', 'going', 'like', 'getting', 
#                    'come', 'felt', 'whatever', 'that', 'come', 'always', 
#                    'also', 'shall', 'thing', 'good', 'maybe', 'thank'])


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


#     # Example
    
#     doc_sample = documents[documents.index == 2].values[0][0]

#     print('original document: ')
#     print(doc_sample)
#     print('\n\n tokenized and lemmatized document: ')
#     print(preprocess_text(doc_sample))

#     processed_sample = preprocess_text(doc_sample)


    # We will apply preprocessing to the whole dataframe
    
    import swifter # Makes applying to datframe as fast as vectorizing

    processed_docs = documents['full_content'].swifter.apply(preprocess_text).to_frame('processed_text') 
    
    
    """
    To get full "dictionary" -- for word frequencies
    """
    
    all_processed_docs_list = processed_docs.processed_text.to_list() # Converts all rows to one big list of lists
    all_processed_docs_list = [item for sublist in all_processed_docs_list for item in sublist] # List of lists to one simple list
    
    
    
    # Function for word frequencies
    
    def get_frequency(processed_text_list): 
        
        """
        An NLTK function
        Gets frequency distribution of all words in a tokenized list
        We also sort these frequencies in descending order
        """
    
        word_frequency = FreqDist(word for word in processed_text_list)

        sorted_counts = sorted(word_frequency.items() , key = lambda x: x[1] ,
                                   reverse = True)

        return sorted_counts
    
    
    all_docs_frequency = get_frequency(all_processed_docs_list) 
    
    
#     for i in all_docs_frequency:
#         print(i)


#     Gensim's in-built dictionary

    text_dictionary = gensim.corpora.Dictionary(processed_docs)
    
    """
    gensim has its own high and low pass filters as shown below.
    However, we are unable to see exactly which words were removed.
    """

    # Include words in dictionary that appear greater than 5 times - Low pass
    # but less than 0.5 proportion of the frequency of all the words in all of the articles - High pass

    text_dictionary.filter_extremes(no_below = 5, no_above=0.5) 
    print(len(text_dictionary))
    
    
    """
    All the words have been mapped to an "ID" using gensim.corpora.Dictionary
    Now, within each individual "document" (news article), we can get the corresponding word counts.
    Unfortunately, gensim only allows for getting document-level word frequencies.
    """

    main_corpus = [text_dictionary.doc2bow(doc) for doc in processed_docs]
    
    
    # TF-IDF on the bag of words corpus

    from gensim import models

    tfidf = models.TfidfModel(main_corpus)
    tfidf_main_corpus = tfidf[main_corpus]
    
    
    
    
    """
    Now, do LDA
    
    """



    

# ------------------------------------------------------------------------------





# In[ ]:




