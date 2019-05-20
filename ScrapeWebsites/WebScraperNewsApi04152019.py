"""
Shane Bookhultz
April 15th, 2019 
Web Scraper to compare LDA from these links to the full text
Possibly in the future use each days text to solve
Websites focused on:
Global: AP, WSJ, USA-Today, CBS, ABC, Washington Post, NBC,
NYT, CNN, Huff post, MSNBC, Breitbart, Fox
"""


from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import requests
import csv
import time

start=time.time()
# Need to read in file links

#readfile = "AllUrls03042019.txt"
#savefile = "CompleteContent03042019.txt"

#readfile = "AllUrls22019-02-062019-02-27.txt"
#savefile = "CompleteContent0206-0227.txt"

#readfile = "C:/Users/USER/Documents/Save20190302/NewsMar022019-03-02Total3087.csv"
#savefile = "C:/Users/USER/Documents/Save20190302/AllContent2019-03-02.csv"

readfile = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/Save20190313/NewsMar132019-03-13Total5349.csv"
savefile = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/Save20190313/AllContent2019-03-13.csv"



##########################################################
# This section is for Local news sources: files
##########################################################

# The setup of the articles are
# Title: h1 tag, itemprop = "headline"
# Time&Date: time tag, class="tnt-date asset-date text-muted
# Author: span tag, itemprop="author" class="tnt-byline"
# Text: div itemprop="articleBody" then p tags

# fread = open(readfile,"r")
# listurls = []
# for link in fread:
#     listurls.append(link)

# type(listurls)
 
# newlist = [i.split(' ') for i in listurls]

# listurls = newlist[0]

# Now this is a list with 17k links


    
# Now I have all the links in a list
    
# Idea: Use requests to get a file of links off of search pages, then use that to filter into here
# For right now, I will assume that I have a file that has all the links
# Consider using requests to get all the links off of a searching page, then getting the text
# Might use a csv format to save each file

# For now, I'm just going to be pulling the title and text in the document

########################################3
# Problems with using this requests
# 1. Encoding issues
# 2. Get this error: ContentDecodingError: ('Received response with content-encoding: gzip, but failed to decode it.', error('Error -3 while decompressing data: incorrect header check',))

####################################
# New section for csv reading in
####################################
file = open(readfile, encoding="utf8")
csv_reader = csv.reader(file)
firstrow = next(csv_reader)
firstrow.append("full_content")
alltext = []
alltext.append(firstrow)
#csv_reader = csv_reader(csv_file, delimiter=",")
#fieldnames = ["source_id","source_name","author","title","description","url","urlToImage","publishedAt","content"]   csv_reader = pandas.read_csv(readfile)
# Think about whether to use read_csv or pandas to read and add the additional column to the csv
#wfile = open(savefile,"w+")
#csv_writer = csv.writer(wfile,lineterminator='\n')
i =0

from joblib import Parallel, delayed
import multiprocessing as mp

numcores = mp.cpu_count()



def readrow(row):
    url = row[5]
    rget = requests.get(url)
    mytext = BeautifulSoup(rget.text, "html.parser")
    # I'm going to need to change this to be per type of article
    # Check to see if it returns an empty string
    
    #########################################
    # Sources this works on USA Today, Breitbart, CBS News
    # CNN is a little more difficult
    # Fox News is good, MSNBC -> look at p tags, most are videos
    # NBC News is good, NYT is good
    # Wall Street Journal might be paywalled - but it is article p
    # Washington Post is good, watch for removal of pages
    # Huffpost works for article p
    #########################################
    # ABC News just ha now-playing not much details
    ptags = mytext.select("article p")
    if (ptags==[]):
        # For AP
        ptags = mytext.find_all("div", attrs={"class": "Article"})
    if (ptags==[]):
        # For CNN
        ptags = mytext.find_all("section",attrs={"id":"body-text"})
    ptaglist = []
    for ptag in range(len(ptags)):
        out = UnicodeDammit(ptags[ptag].get_text())
        ptaglist.append(out.unicode_markup)

    joinedtext = ' '.join(ptaglist)
    writestr = joinedtext.replace('\n', ' ').replace('\r','').replace('\t', ' ').replace('\\', '')
    row.append(writestr)
 #   csv_writer.writerow(row)    
    alltext.append(row)
    i = i + 1
    #if(i ==75):
    #    break
    print(i) 
    return savefile

savefile = Parallel(n_jobs=(numcores-1)(delayed(readrow)(row) for row in csv_reader))

for row in csv_reader:
# The urls are in the 6th column, so fifth index    
    url = row[5]
    rget = requests.get(url)
    mytext = BeautifulSoup(rget.text, "html.parser")
    # I'm going to need to change this to be per type of article
    # Check to see if it returns an empty string
    
    #########################################
    # Sources this works on USA Today, Breitbart, CBS News
    # CNN is a little more difficult
    # Fox News is good, MSNBC -> look at p tags, most are videos
    # NBC News is good, NYT is good
    # Wall Street Journal might be paywalled - but it is article p
    # Washington Post is good, watch for removal of pages
    # Huffpost works for article p
    #########################################
    # ABC News just ha now-playing not much details
    ptags = mytext.select("article p")
    if (ptags==[]):
        # For AP
        ptags = mytext.find_all("div", attrs={"class": "Article"})
    if (ptags==[]):
        # For CNN
        ptags = mytext.find_all("section",attrs={"id":"body-text"})
    ptaglist = []
    for ptag in range(len(ptags)):
        out = UnicodeDammit(ptags[ptag].get_text())
        ptaglist.append(out.unicode_markup)

    joinedtext = ' '.join(ptaglist)
    writestr = joinedtext.replace('\n', ' ').replace('\r','').replace('\t', ' ').replace('\\', '')
    row.append(writestr)
 #   csv_writer.writerow(row)    
    alltext.append(row)
    i = i + 1
    #if(i ==75):
    #    break
    print(i)
#htmlsavepath = "./rawHTMLdir/"
#articlesavepath = "./ArticlesForFeb13/"

wfile = open(savefile,"w+",encoding="utf8")
csv_writer = csv.writer(wfile,lineterminator='\n')
csv_writer.writerows(alltext)
file.close()
wfile.close()

end=time.time()

print(end-start)
# savelist = []
# failcounter = 0
# #overallfile = open(savefile,"a+",encoding="utf-8")
# for j in range(len(listurls)):
#     print(j)
#     overallfile = open(savefile,"a+",encoding="utf-8")
#     # So the program fails here, with an error on the 16th link
#     try:
#         rget = requests.get(listurls[j])
#         savelist.append(BeautifulSoup(rget.text,"lxml"))
#         # I'm just going to save the content of these links
#         webptag = savelist[j].select("article p") # I might want to make this general to p in the future    
#         ptaglist = []
#         for ptag in range(len(webptag)):
#             ptaglist.append(webptag[ptag].get_text())
            
#         ptagstr = ' '.join(ptaglist)
#         #writelist = []
#         #writelist.extend((webtitle,ptagstr))
#         #writestr = ' '.join(writelist)
#         writestr = ptagstr.replace('\n', ' ').replace('\r','').replace('\t', ' ')
#         #fullpath = articlesavepath + str(iter1) + str(i) + ".txt"
#         #wfile = open(fullpath,"w+",encoding="utf-8")
#         #wfile.write(writestr)
#         #wfile.close()
#         writenewline = writestr + "\n"
#         # And then with the own files, I'm going to also add to the overall Text file
#         overallfile.write(writenewline)
#         overallfile.close()
#     except: 
#         failcounter = failcounter + 1
#         print(("Fail number:"+ str(failcounter)))
#         overallfile.close()
#         #break
# # Why is this failing every single one?




