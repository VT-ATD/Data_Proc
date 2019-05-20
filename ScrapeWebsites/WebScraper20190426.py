"""
Shane Bookhultz
April 25th, 2019 
Web Scraper to compare LDA from these links to the full text
Possibly in the future use each days text to solve
Websites focused on:
Global: AP, WSJ, USA-Today, CBS, ABC, Washington Post, NBC,
NYT, CNN, Huff post, MSNBC, Breitbart, Fox

4/25 Update to autonomously do this 
"""


from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import requests
import csv
import time
import os
import glob
import random

#start=time.time()
# Need to read in file links

#readfile = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/Save20190313/NewsMar132019-03-13Total5349.csv"
#savefile = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/Save20190313/AllContent2019-03-13.csv"


##########################################################
# This section is for Local news sources: files
##########################################################

####################################
# New section for csv reading in
####################################

#dirpath = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-"
#startingfolder = "/Save20190312"

# Then get all csv files in that one folder
def readarticle(URL):
  rget = requests.get(URL)
  mytext = BeautifulSoup(rget.text,"html.parser")
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
  return (writestr)

#def list_files(dir):
#  r = []
#  for root, dirs, files in os.walk(dir):
#    for name in files:
#      r.append(os.path.join(root,name))
#  return r

def list_csvs(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                files.append(os.path.join(r, file))
    return files
# maybemake a function for new days
    
def main():
    startind = 66 # was 22, 32, 40 # Need to start with 4/3 now
    a = 0
    endnotif = "End of file"
    timefile = "TimesApr04-May05.txt"
    timeopen = open(timefile,"w+")
    timesavelist = []
    dirpath = "C:/Users/USER/Documents/ATD Group Spring 2019/NewsDataFilesMar02-/"  
    allfiles = list_csvs(dirpath)
  # Find a starting path
    for fileind in range(startind,len(allfiles),2):
        i = 1
        interlist = [] # intermediate list to save the date and time
        starttime = time.time()
        correctfile = allfiles[(fileind+1)].replace('\\','/')
        f = open(correctfile,encoding="utf-8")
        csv_reader = csv.reader(f)
        firstrow = next(csv_reader)
        firstrow.append("full-content")
        alltext = []
        alltext.append(firstrow)
        for row in csv_reader:
            url = row[5]
            try: 
                mywrite = readarticle(url)
            except:
                mywrite= ""
            row.append(mywrite)
            alltext.append(row)
            if(i % 10 ==0):
                print(i)
            i = i + 1
        writefile = allfiles[fileind].replace('\\','/')
        wfile = open(writefile,"w+",encoding="utf8")
        csv_writer = csv.writer(wfile,lineterminator='\n')
        csv_writer.writerows(alltext)
        endtime = time.time()
        interlist.append(writefile.replace(dirpath,"")[4:12])
        interlist.append(str(endtime-starttime))
        timesavelist.append(' '.join(interlist))
        a = a + 1
        f.close()
        wfile.close()
        print(endnotif)
        print(fileind)
        # sleep here
        time.sleep(random.randint(1,60))
    
    savetimefile = '\n'.join(timesavelist)
    timeopen.write(savetimefile)
    timeopen.close()

if __name__ == '__main__':
    main()

#for row in csv_reader:
#  # The urls are in the 6th column, so fifth index    
#  url = row[5]
#  rget = requests.get(url)
#  mytext = BeautifulSoup(rget.text, "html.parser")
#  # I'm going to need to change this to be per type of article
#  # Check to see if it returns an empty string
#  
#  #########################################
#  # Sources this works on USA Today, Breitbart, CBS News
#  # CNN is a little more difficult
#  # Fox News is good, MSNBC -> look at p tags, most are videos
#  # NBC News is good, NYT is good
#  # Wall Street Journal might be paywalled - but it is article p
#  # Washington Post is good, watch for removal of pages
#  # Huffpost works for article p
#  #########################################
#  # ABC News just ha now-playing not much details
#  ptags = mytext.select("article p")
#  if (ptags==[]):
#    # For AP
#    ptags = mytext.find_all("div", attrs={"class": "Article"})
#  if (ptags==[]):
#    # For CNN
#    ptags = mytext.find_all("section",attrs={"id":"body-text"})
#  ptaglist = []
#  for ptag in range(len(ptags)):
#    out = UnicodeDammit(ptags[ptag].get_text())
#  ptaglist.append(out.unicode_markup)
#  
#  joinedtext = ' '.join(ptaglist)
#  writestr = joinedtext.replace('\n', ' ').replace('\r','').replace('\t', ' ').replace('\\', '')
#  row.append(writestr)
#  #   csv_writer.writerow(row)    
#  alltext.append(row)
#  i = i + 1
#  #if(i ==75):
#  #    break
#  print(i)
##htmlsavepath = "./rawHTMLdir/"
##articlesavepath = "./ArticlesForFeb13/"
#
#wfile = open(savefile,"w+",encoding="utf8")
#csv_writer = csv.writer(wfile,lineterminator='\n')
#csv_writer.writerows(alltext)
#file.close()
#wfile.close()
#
#end=time.time()
#
#print(end-start)