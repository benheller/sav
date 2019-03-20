import markovify
import requests
import html2text
import json
import time
import functools
import random
import sys
import argparse
import tweepy
import re
import os

## args

parser = argparse.ArgumentParser()
parser.add_argument('topic')
parser.add_argument('-k', '--api-key', required=True)
parser.add_argument('-u', '--user', default='sav')
parser.add_argument('-c', '--chaos', action='store_true')
parser.add_argument('--debug', action='store_true')
settings = parser.parse_args()

## opts

h = html2text.HTML2Text()
h.ignore_links = True

print ('LOG: Initializing รคש...')

for arg in vars(settings):
    print('OPTION:', '%s == %s' % (arg, getattr(settings, arg)))

headers = {
    'accept': 'application/json'
}

payload = {
    "api_username": settings.user,
    "api_key": settings.api_key
}

# Twitter ends up not being a good Markov source
# Leaving this here (and throughout) so others can experiment...
# auth = tweepy.OAuthHandler('', '')
# auth.set_access_token('', '')
# api = tweepy.API(auth)

## methods

def with_logging(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        action = 'Debugging' if settings.debug else 'Running'
        completion = 'printed to console' if settings.debug  else 'completed'
        print('LOG: %s job "%s"' % (action, func.__name__))
        result = func(*args, **kwargs)
        print('LOG: Job "%s" %s' % (func.__name__, completion))
        return result
    return wrapper


def sanitize(text, fromHtml):

    if (fromHtml):
        text = h.handle(text['cooked'])

    if (text.startswith('>')):
        return
    
    if (text.startswith('RT')):
        return

    text = text.replace('\n', ' ')
    text = re.sub(r"http[s]?://\S+", '', text)
    text = re.sub(r"@\S+", '', text)

    return text


def get_text(name): 
    try:
        r = requests.get('https://discourse.ecult.org/users/%s/activity.json' %name, params=payload, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print ('ERROR:', err)
        sys.exit(1)
    posts = r.json()
    valid_posts = list(filter(None, [sanitize(p, True) for p in posts]))
    return valid_posts

# def get_tweets(name):
#     tweets = api.user_timeline(name)
#     valid_tweets = list(filter(None, [sanitize(t.text, False) for t in tweets]))
#     return '. '.join(valid_tweets)

def get_post():
    seb_model = markovify.Text(get_text('seb'))
    dav_model = markovify.Text(get_text('dav'))

    # Unused Twitter code
    # twitter_model = markovify.Text(get_tweets(''))

    if (settings.chaos):
        path = os.path.join(os.path.dirname(__file__), 'sources/fred_durst.txt')
        with open(path) as f:
            chaos_text = f.read()
        chaos_model = markovify.Text(chaos_text)
        combined_model = markovify.combine([seb_model, dav_model, chaos_model], [1, 1, 2])
    else:
        combined_model = markovify.combine([seb_model, dav_model])

    sentences = []

    for _ in range(random.randint(1, 12)):
        sentences.append(combined_model.make_sentence())
        if (random.random() < 0.3):
            sentences.append('\n\n')

    return ' '.join(sentences)


@with_logging
def make_post():
    body = dict(payload, **{
        "topic_id": settings.topic,
        "raw": get_post()
    })

    print('LOG:', body)

    if (settings.debug == False):
        return requests.post('https://discourse.ecult.org/posts.json', data=body)

## implementation

make_post()
