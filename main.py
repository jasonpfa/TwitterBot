import gspread
import tweepy
import re
import collections
import itertools
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import pandas as pd

# Twitter Credentials ----------------------------------------------------------------
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAKwZZQEAAAAAHjWOGDd5T%2B3MVcqD0ThVzJQj6Hk%3DOS8zFoocNUNUBAN0HlEQibG6zhp4u6R7ktnU3ZVwdhia2GnDY6'
access_token = '3140921509-f3PaV0zNmF31RvoqrHhTVR0pJjtI8begDOKeS6W'
access_token_secret = 'X26fEYvSZylfCooEL7fCgTJjn1dEZLp8F68BHmTDBisbF'
consumer_key = '6uYwIXYQGrbhwq4gKNuDtcqYd'
consumer_secret = 'GlxAeCaZHicpt3vdl2BMRvQEGI0k4XvKGc05se8vi1AfxxVDHU'

client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
gc = gspread.service_account('gscredentials.json')


def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

# Script ----------------------------------------------------------------------
# Open a spreadsheet
ss = gc.open('Twitter_Bot')
# Open a sheet from a spreadsheet
fresh = ss.get_worksheet(0)
archive = ss.get_worksheet(1)
# Read next tweet from sheets
next_query = fresh.acell('B2').value
# Define query/start time/end time/ number of tweets
next_query_clean = next_query + " -is:retweet -is:reply"
start_time = datetime.datetime.now() - timedelta(days=1)
end_time = datetime.datetime.now() - timedelta(seconds=11)
max_results = 100

tweets = client.search_recent_tweets(query=next_query_clean,
                                     start_time=start_time,
                                     end_time=end_time,

                                     tweet_fields=["context_annotations", "created_at", "public_metrics"],
                                     max_results=max_results,
                                     expansions='author_id'
                                     )
all_tweets = [tweet.text for tweet in tweets.data]
all_tweets_no_urls = [remove_url(tweet) for tweet in all_tweets]
words_in_tweet = [tweet.lower().split() for tweet in all_tweets_no_urls]

# Remove stop words
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
for all_words in words_in_tweet:
    for word in all_words:
        tweets_nsw = [[word for word in tweet_words if not word in stop_words]
                      for tweet_words in words_in_tweet]
# Remove collection words
collection_words = [next_query]
tweets_nsw_nc = [[w for w in word if not w in collection_words]
                 for word in tweets_nsw]
all_words_nsw_nc = list(itertools.chain(*tweets_nsw_nc))
# Create counter
counts_nsw_nc = collections.Counter(all_words_nsw_nc)
print(counts_nsw_nc.most_common(15))

# # Create panda dataframe
# clean_tweets_ncw = pd.DataFrame(counts_nsw_nc.most_common(15),
#                              columns=['words', 'count'])
# clean_tweets_ncw.head()
# fig, ax = plt.subplots(figsize=(8, 8))
# # Plot horizontal bar graph
# clean_tweets_ncw.sort_values(by='count').plot.barh(x='words',
#                       y='count',
#                       ax=ax,
#                       color="blue")
#
# ax.set_title("Common Words Found in Tweets (Without Stop or Collection Words)")
# plt.savefig('words.png')

# Get next word
new_word = counts_nsw_nc.most_common(1)[0][0]
# Post tweet through twitter API
response = client.create_tweet(text="Word Used : " + next_query + "\nWord Winner: " + new_word)
# Delete row on success
fresh.delete_rows(2)
# # Move row to archive on success
# Get the next row in the archive
archive_list = archive.col_values(1)
next_row = int(archive_list[-1]) + 2
# Update archive with tweet and time
archive.update_cell(next_row, 1, next_row - 1)
archive.update_cell(next_row, 2, next_query)
archive.update_cell(next_row, 3, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

# # Add new word
# Get the next row in fresh
fresh_list = fresh.col_values(1)
next_row = int(fresh_list[-1]) + 2
print(next_row)
fresh.update_cell(next_row - 1, 1, next_row - 1)
fresh.update_cell(next_row - 1, 2, new_word)
for n in range(1, next_row - 1):
    fresh.update_cell(next_row - n, 1, (next_row - n) - 1)

