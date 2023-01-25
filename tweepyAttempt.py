import tweepy
import numpy as np
import pandas as pd
import yaml
import csv
from time import sleep, localtime

with open('.twitter_keys.yaml', 'r') as file:
    priv_keys = yaml.safe_load(file)
bToken = priv_keys['search_tweets_v2']['bearer_token']

#set up BERT
from codeswitch.codeswitch import LanguageIdentification
lid = LanguageIdentification('hin-eng')  
threshold = 0.75

#get cities
india_states = pd.read_csv('./india_states_capitals.csv')
india_states = india_states.loc[0:28, ["LargestCity", "Lat", "Long"]]

#set up date structure
begin_date = pd.to_datetime("Nov 6th, 2012")
end_date = pd.to_datetime("Nov 6th, 2020")
date_r = pd.date_range(start = begin_date, end = end_date, freq= "Q" )

def makeQuery(llat, llong, datePoint, dayOffset):
    details = "point_radius:[" + str(llong) + " " + str(llat) + " 3mi]"
    startDate = pd.to_datetime(datePoint) -  pd.to_timedelta(dayOffset, unit='d')
    endDate = pd.to_datetime(datePoint) +  pd.to_timedelta(dayOffset, unit='d')
    return (details, startDate, endDate)

#open result files
tweetsFile = open("./tweepyResults/by_milestones_2224.csv", "a", newline="", encoding='utf-16')
issuesFile = open("./tweepyResults/by_milestones_issues_2224.csv", "a", newline="", encoding='utf-16')
tweetsWriter = csv.writer(tweetsFile)
issuesWriter = csv.writer(issuesFile)

#set up twitter client
#wait_on_rate_limit 
my_client = tweepy.Client(bToken, wait_on_rate_limit = True)


for index, row in india_states.iterrows():
    still_need = [25,26,27,28]
    print(index)
    retryCount = 0
    if (index not in still_need):
        continue
    for date in date_r:
        #get tweet
        new_search_query = makeQuery(row["Lat"], row["Long"], date, 10)
        
        sleep(1)
        twit_r = my_client.search_all_tweets(query =  new_search_query[0], 
                                        max_results = 50,
                                        tweet_fields = 'text,geo,created_at,lang,source',
                                        expansions = 'geo.place_id',
                                        place_fields = 'id,country,country_code,geo,name,place_type',
                                        start_time = new_search_query[1],
                                        end_time = new_search_query[2])
        try:
            for tweet in twit_r.data:
                retryCount = 0 #reset the retry after a successful call
                #enter bert consensually
                langs_dict = {}
                cEN = cTOTAL = cHIN = 0
                from_Bert = lid.identify(tweet.text)
                # issues_entry = {'issues': []}
                # issues_entry['tweet'] = tweet
                # issue_flag = False

                for item in from_Bert:
                    l = item["entity"]
                    cTOTAL +=1
                    if (l == "en"):
                        cEN +=1
                    elif (l == "hin"):
                        cHIN +=1
                    elif (l in langs_dict):
                        langs_dict[l] +=1
                    else:
                        langs_dict[l] = 1
                    # if (item["score"] < threshold):
                    #     issue_flag = True
                    #     issues_entry['issues'].append(item)

                #write errors to logfile
                # if(issue_flag):
                #     for var in issues_entry["tweet"]:
                #         issuesWriter.writerow(str(var) + issues_entry["tweet"][var])
                #     for iss in issues_entry["issues"]:
                #         issuesWriter.writerow(issues_entry["issues"][iss])

                #error check for missing outputs:
                try:
                    geo = tweet['geo']["coordinates"]["coordinates"]
                except:
                    try:
                        geo = tweet['geo']
                    except:
                        geo = ""

                #write outputs
                tweetCounts_entry = [index, date, tweet['created_at'], geo, tweet['lang'], tweet['source'], cEN, cHIN, cTOTAL, langs_dict]
                tweetsWriter.writerow(tweetCounts_entry)
        except TypeError as e:
            #tweetCounts_entry = [index, date, "", "", "", "", cEN, cHIN, cTOTAL, langs_dict]
            #tweetsWriter.writerow(tweetCounts_entry)
            print(tweet)
            print(str(e))
            continue

        # except tweepy.errors.TooManyRequests:
        #     if (retryCount < 10):
        #         sleep(1)
        #         continue
        #     else:
        #         sleep(900)
        #         print("429 with too many retries, sleeping for 15 mins")
        #         continue

                 
tweetsFile.close()
issuesFile.close()
        
        