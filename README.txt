● Twitter Bot
o Twitter Bot Developed in Python utilizing Google Sheets API, Twitter API, Google Cloud 
Scheduler
o Scrapes recent tweets based on the next query in the Google Sheet and finds the most common 
word (excluding stopwords and collection words) in these tweets
o Adds the new word to the appropriate Sheet and moves the queried word to the archive Sheet
o Posts a tweet containing the word used to query and the new common word found
o Google Cloud Scheduler is used to run this Python function each day at midnight

words.png is a graph representation of the most common words
(utilized in testing not an up to date sample)