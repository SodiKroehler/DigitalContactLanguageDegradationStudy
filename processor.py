import numpy as np
import pandas as pd
import sys
import csv

#recieve a csv
input_stream = open(sys.argv[1], encoding='utf-16')
tweetsFile = open(sys.argv[2], "a", newline="", encoding='utf-16')
issuesFile = open(sys.argv[3], "a", newline="", encoding='utf-16')

#parse into dataframe
india_states = pd.read_csv('india_states_capitals.csv')
input_tweets = pd.read_csv(input_stream)

#enter bert consensually
from codeswitch.codeswitch import LanguageIdentification
lid = LanguageIdentification('hin-eng')  

threshold = 0.75
tweetsWriter = csv.writer(tweetsFile)
issuesWriter = csv.writer(issuesFile)

for index, row in input_tweets.iterrows():
    langs_dict = {}
    from_Bert = lid.identify(row.tweet)
    issues_entry = {'issues': []}
    issues_entry['tweet'] = row
    issue_flag = False

    for item in from_Bert:
      l = item["entity"]
      if (l in langs_dict):
        langs_dict[l] +=1
      else:
        langs_dict[l] = 1
      if (item["score"] < threshold):
        issue_flag = True
        issues_entry['issues'].append(item)

    #write errors to logfile
    if(issue_flag):
      issuesWriter.writerow(issues_entry)

    #write counts to output
    row["counts"] = langs_dict
    tweetCounts_entry = [row["created_at"],row["geo"],row["lang"],row["quote_count"],row["source"],row["counts"]]
    tweetsWriter.writerow(tweetCounts_entry)
tweetsFile.close()
issuesFile.close()
input_stream.close()