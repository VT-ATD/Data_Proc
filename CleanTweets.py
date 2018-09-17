## -*- coding: utf-8 -*-
##  CleanTweets.py
##
##  Takes in a file of twitter data, outputs an analogous file of processed
##  twitter data, along with a subset of the original data.
##
##  Requires file: `blacklist.txt` in the python path.
##                  Blacklist must have one word per line.
##  
##  Use:
##      >> python CleanTweets.py target_json_file
##
##  `target_json_file` requires one json per line, with the minimum field
##       {"body":"This is an original tweet, #datascience"....}
##
##

__author__ = "Peter Hauck"
__email__ = "phauck@vt.edu"


import sys
import os
import sys
import json
import string
import re
import operator
import nltk
from nltk.corpus import stopwords
import numpy as np
from operator import itemgetter
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

token_dict = {}
stemmer = PorterStemmer()
#need this
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#need this
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

def get_tokens(text_list):
    for indx, text in enumerate(text_list):
        lowers = text.lower()
        #remove the punctuation using the character deletion step of translate
        #no_punctuation = lowers.translate(None, string.punctuation)
        tokens = nltk.word_tokenize(lowers)
        text_list[indx] = tokens
    return text_list
#need this
def preprocess(sentence,blacklist):
        sentence = sentence.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        allbadwords = stopwords.words('english') + blacklist
        filtered_words = [w for w in tokens if not w in allbadwords]
        return " ".join(filtered_words)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def is_ascii(s):
    try:
        s.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def main():
 
    try: 
        with open('blacklist.txt') as f:
             blacklist = f.read().splitlines()
        f.close()

    fname_test_tweets = sys.argv[1]
    fname_out = fname_test_tweets +"_prcsd"
    test_set = []

    with open(fname_test_tweets) as f:
         with open(fname_out,'w') as f1:
              for line in f:

                  if is_json(line):
                     j_content = json.loads(line)
                     tweet_message = j_content['body']
                     preprcssd_tweet = preprocess(tweet_message,blacklist)

                     if is_ascii(preprcssd_tweet):
                        prcsd_twt_str = preprcssd_tweet
                        j_content['prcsd_body'] = prcsd_twt_str
                        less_content = {}
                        less_content['prcsd_body'] = prcsd_twt_str
                        less_content['body'] = j_content['body']
                        less_content['gnip'] = j_content['gnip']
                        newline = json.dumps(less_content)+"\n"
                        f1.writelines(newline)
                     else:
                        print 'Non-English Tweet Passed though Filtration', tweet_message
    f.close()



if __name__ == '__main__':
    main()

