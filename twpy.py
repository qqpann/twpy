#!/usr/bin/env python3
from requests_oauthlib import OAuth1Session
import json
import argparse
import os.path
from math import log10 as log
from datetime import datetime as dt


USAGE = '''
[-tw text]  tweet text
[-tl]       show timeline'''
DESCR = '''With this, you can tweet from the terminal.'''
def prep_args():
    parser = argparse.ArgumentParser(description=DESCR,
                                     usage=USAGE)
    parser.add_argument('-tw', '--tweet', help='tweet text', required=False)
    parser.add_argument('-tl', '--timeline',
                        action='store_true', help='view TL', required=False)
    args = parser.parse_args()
    return args


def get_timeline():
    '''get timeline'''
    C = lambda n: '\033[%sm' % str(n)
    BLCF = C(30)
    BLUF = C(32)
    REDF = C(31)
    GRYB = C(40)
    BLCB = C(100)
    LGRB = C(107)
    ENDC = C(0)

    url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    params = {'count': 200}
    req = twitter.get(url, params=params)
    if req.status_code == 200:
        # api limit info
        limit = int(req.headers['x-rate-limit-remaining'])
        reset = int(req.headers['x-rate-limit-reset'])
        print('===== timeline =====')
        print('lmt:', '*'*limit + '.'*(15-limit))
        print('rst:', dt.fromtimestamp(reset).strftime('%m/%d %H:%M'))
        print('====================')
        # timeline
        timeline = json.loads(req.text)
        counter = 0
        for tweet in timeline:
            if tweet['retweet_count']>5 or tweet['favorite_count']>10:
                LC = C('48;5;236') if counter % 2 == 0 else C('48;5;232')
                SC = C('38;5;255') if counter % 2 == 0 else C('38;5;249')
                rt, fv = tweet['retweet_count'], tweet['favorite_count']
                print(LC+BLUF+ '%1.1f'%log(rt + 1) +' '+ENDC,
                      LC+REDF+ '%1.1f'%log(fv + 1) +' '+ENDC,
                      LC+SC+tweet['text'].replace('\n', '\u21a9 '),
                      sep='', end='\n'+C(49))
                counter += 1
                if counter > 14:
                    break
    else:
        print('Error: %d' % req.status_code)


def post_tweet(text):
    '''post a tweet'''
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {'status': text}
    req = twitter.post(url, params=params)
    if req.status_code == 200:
        print('Success')
    else:
        print('Error: %d' % req.status_code)


if __name__ == '__main__':
    proj_dir = os.path.expanduser('~/workspace/projects/tweet_py/')
    with open(proj_dir+'secrets.json', 'r') as f:
        _tokens = json.load(f)
    twitter = OAuth1Session(*_tokens)
    args = prep_args()
    if args.tweet:
        print('=== tweet ===')
        text = args.tweet
        post_tweet(text)
    elif args.timeline:
        get_timeline()
    else:
        print(USAGE)
