import tweepy
import time
import datetime
import random
import fnmatch

# Twitter credentials stored in separate file
import twitter_credentials

auth = tweepy.OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
user = api.me()

# Twitter user to generate tweet content from
target = '@twitteruser'

# List of words that the bot will look for in users tweets to replace (case sensitive)
key_phrases_match_list = ['*KeyWord1*','*KeyWord2*']

# Dictionary with Keys of words from tweet and Values of replacment words/phrases
key_phrases_dict = {'*KeyWord1*' : 'Replacement Word1',
                    '*KeyWord2*' : 'Replacement Word2',
                    '*&amp;*' : '&',}

# second dictionary to cover cases where tweet length goes over 280 chars due to replacment words being longer than original
key_phrases_dict2 = {'*KeyWord1*' : 'NewWord1',
                    '*KeyWord2*' : 'NewWord2',
                    '*&amp;*' : '&'}

# List of last N number of tweets on bots own timeline
lastN_tweets = []

# Func to generate list of tweets on own timeline to check new tweets against
def own_tweets():
    tweets = api.user_timeline(count=10,tweet_mode="extended")
    for tweet in tweets:
        if fnmatch.fnmatch(tweet.full_text, '*&amp;*'):
            tweet = tweet.full_text.replace('&amp;' , '&')
            lastN_tweets.extend([tweet])
        else:
            lastN_tweets.extend([tweet.full_text])
    return lastN_tweets


# grab targets tweets to use as content to swap words out
target_tweets = api.user_timeline(id = target,count=20, tweet_mode="extended")

# replace dictionary keys with dictionary values
def replace_words(og_tweet):
    now = datetime.datetime.now().isoformat()
    print(f'{now} replacing words...')
    new_tweet = og_tweet
    if len(new_tweet) <= 270:
        for key in key_phrases_dict.keys():
            if fnmatch.fnmatch(og_tweet, key):
                phrase_key = key[1:-1]
                phrase_value = key_phrases_dict[key]
                new_tweet = new_tweet.replace(phrase_key, phrase_value)
    else:
        for key in key_phrases_dict2.keys():
            if fnmatch.fnmatch(og_tweet, key):
                phrase_key = key[1:-1]
                phrase_value = key_phrases_dict2[key]
                new_tweet = new_tweet.replace(phrase_key, phrase_value)
    return new_tweet

# ignore retweets & check targets tweets for key words, call replace_words and check against own timeline for duplicate tweets
def totally_real_news():
    now = datetime.datetime.now().isoformat()
    print(f'{now} scanning for tweets...')
    for tweet in target_tweets:
        if 'RT' in tweet.full_text:
            continue
        else:
            try:
                for phrase in key_phrases_match_list:
                    if fnmatch.fnmatch(tweet.full_text, phrase):
                        new_tweet = replace_words(tweet.full_text)
                        TFFlag = any(new_tweet in x for x in lastN_tweets)
                        TFFlag = not TFFlag
                        if TFFlag and len(new_tweet) <= 280:
                            now = datetime.datetime.now().isoformat()
                            print(f'{now} tweeting..')
                            api.update_status(new_tweet)
                            lastN_tweets.extend([new_tweet])
                        else:
                            print('already tweeted')
            except tweepy.error.TweepError as e:
                print(e)


own_tweets()
totally_real_news()
