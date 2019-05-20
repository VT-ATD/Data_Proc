"""
Shane Bookhultz
5/1/19
Preprocess05012019.py
Goal: Stem documents, make columns of csv file into stemmed output
Columns will be made of: there will be content, full-content, and shortonlong-content
"""

# First need to read in the csv
# Will automate in the future

#import textblob
import csv
#import os
import time
from textblob import TextBlob
from textblob import Word


def getVocab(csvobj,ind):
    vocab = set()
    for row in csvobj:
        # Convert each row into word
        blob = TextBlob(row[ind])
        for w in range(len(blob.words)):
            theword = Word(blob.words[w]).stem() # will need to go through each word and stem
            vocab.add(theword)
    return vocab    

def main():
    filename = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/Save20190302/AllContent2019-03-02.csv"
    f = open(filename,encoding='utf-8')
    csv_read = csv.reader(f)
    allvocabset = getVocab(csvobj = csv_read,ind = 8) # 8 for short content
    # All vocab set works
    f.close()
    f = open(filename,encoding='utf-8')
    csv_reader = csv.reader(f)
    firstrow = next(csv_reader)
    firstrow.append("shortprocessed-content")
    firstrow.append("fullprocessed-content")
    firstrow.append("shortonlong-content")
    alltext = []
    alltext.append(firstrow)
    starttime = time.time()
    globali = 0
    #print(1)
    for roww in csv_reader: # it doesn't go through this loop?
        #print(500)
        #print(roww)
        rowdoc1 = list()
        rowdoc2 = list()
        rowdoc3 = list()
        blobshort = TextBlob(roww[8])
        bloblong = TextBlob(roww[9])
        #print(501)
        for wshort in range(len(blobshort.words)):
            wordshort = Word(blobshort.words[wshort]).stem()
            rowdoc1.append(wordshort)
        for w in range(len(bloblong.words)):
            myword = Word(bloblong.words[w]).stem()
            rowdoc2.append(myword)
            if(myword in allvocabset):
                rowdoc3.append(myword)
        rowdoc1 = ' '.join(rowdoc1)
        rowdoc2 = ' '.join(rowdoc2)
        rowdoc3 = ' '.join(rowdoc3)
        roww.append(rowdoc1)
        roww.append(rowdoc2)
        roww.append(rowdoc3)
        alltext.append(roww)
        globali = globali + 1
        print(globali)
    # Now I need to write to this csv
    writefile="C:/Users/USER/Documents/ATD Group Spring 2019/StoreProcessedArticles/ProcessedData2019-03-02redo.csv"
    wfile = open(writefile,"w+",encoding="utf8")
    csv_writer = csv.writer(wfile,lineterminator='\n')
    csv_writer.writerows(alltext)    
    endtime = time.time()
    print(endtime-starttime)
    f.close()
    wfile.close()

if __name__ == '__main__':
    main()
    
        # Now go through and append to the csv file
        
    # Once we have the reader