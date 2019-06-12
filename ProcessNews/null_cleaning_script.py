
import glob
import os
import pandas as pd 
import re
from pandas import Series, DataFrame

directory = "/home/sdbookhu/FullNews/"

#directory = "C:/Users/Shreya/Desktop/all un news/"

for files in glob.glob(directory+'*.csv'):

    print(files[35:])

    news_source = []
    news_title = []
    news_description = []
    news_url = []
    news_publish_time = []
    news_content = []
    news_full_content = []

    save_directory = "/home/shreyac/cleaned_news/"

    #save_directory = "C:/Users/Shreya/Desktop/all pro news/"

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


    for i in range(0, len(data_all)):

        news_url.append(data_url[i])
        news_source.append(data_source[i])
        news_publish_time.append(data_publish_time[i])
        news_title.append(data_title[i])
        news_description.append(data_description[i])
        news_content.append(data_content[i])
        news_full_content.append(data_full_content[i])


    news_file_df = DataFrame({'url': news_url,
                    'source': news_source,
                    'published_at': news_publish_time,
                    'title': news_title,
                    'description': news_description,
                    'content': news_content,
                    'full_content': news_full_content})

    news_file_df = news_file_df[['url', 'source', 'published_at', 'title',
                                     'description', 'content', 'full_content']]

 

    save_directory = save_directory + name
    print(save_directory)

    export_csv = news_file_df.to_csv (save_directory, index = None, header=True)

