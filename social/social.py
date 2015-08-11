"""a series of functions for accessing social data"""
import base64
import time
import re
import json
import requests
import urllib

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


facebook_client_id = "803843903065087"
facebook_client_secret = "ad8b95ab5348031963a4ed755b87802f"

twitter_consumer_key = "MdmA3DXBBBnUSzcsmhtNLQ"
twitter_consumer_secret = "AmAiPpunUhCQAOIndLjrmzEuIHOBIGbcWmxGAmhmwQk"

def facebook_access_token():
    access_token_url = ("https://graph.facebook.com/oauth/access_token?client_id"
                "={client_id}&client_secret={client_secret}&grant_type=client_cr"
                "edentials&redirect_uri=#").format(
            client_id=facebook_client_id,
            client_secret=facebook_client_secret)
    r = requests.get(access_token_url)
    return re.search(r'access_token=(.*)', r.text).groups()[0]

def search_facebook(access_token, query, args):
    """example: search_facebook(..., query="philz coffee", {'type':'page',...})
    """
    search_url = ("https://graph.facebook.com/search?q={query}"
                  "&{args}"
                  "&access_token={access_token}").format(
            query=query.replace(' ', '+'),
            args="&".join(["%s=%s"%(k,v) 
                          for k,v in args.iteritems()]),
            access_token=access_token)
    r = requests.get(search_url)
    return json.loads(r.text)

def twitter_access_token():
    """encode the consumer key and secret and obtain a bearer access token"""
    bearer_token_credentials = "{key}:{secret}".format(key=twitter_consumer_key, 
                        secret=twitter_consumer_secret)
    bearer_token_encoded = base64.b64encode(bearer_token_credentials)

    headers = {
        'Authorization': 'Basic %s' % bearer_token_encoded,
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    payload = {
        'grant_type':'client_credentials',
    }
    r = requests.post("https://api.twitter.com/oauth2/token", 
                      headers=headers,
                      data=payload)
    return json.loads(r.text)['access_token']

def search_twitter(access_token, query):
    search_url = ("https://stream.twitter.com/1.1/statuses/filter.json?"
                  "track={query}").format(query=query)
    search_url = urllib.quote(search_url)

    #params for request
    oauth_consumer_key     = twitter_consumer_key
    oauth_nonce            = base64.b64encode(os.urandom(32))
    oauth_signature_method = "HMAC-SHA1"
    oauth_timestamp        = "%s" % int(time.time())
    oauth_token            = access_token
    oauth_version          = "1.0"

    #create the authorization signature
    auth_sig_params = {
        "track": query,
        "oauth_consumer_key": oauth_consumer_key,
        "oauth_nonce": oauth_nonce,
        "oauth_signature_method": oauth_signature_method,
        "oauth_timestamp": oauth_timestamp,
        "oauth_token": oauth_token,
        "oauth_version": oauth_version,
    }
    
    auth_sig = "{method}&{url}&{auth_sig_params}".format(method="POST",
        url=search_url,
        auth_sig_params = urllib.urlencode(auth_sig_params))

    headers = {
        'Authorization': ('OAuth oauth_consumer_key="{oauth_consumer_key}",'
                          'oauth_nonce="{oauth_nonce}",'
                          'oauth_signature="{oauth_signature}",'
                          'oauth_signature_method="{oauth_signature_method}",'
                          'oauth_timestamp="{oauth_timestamp}",'
                          'oauth_token="{oauth_token}",'
                          'oauth_version="{oauth_version}"').format(
                    oauth_consumer_key=twitter_consumer_key,
                    oauth_nonce=base64.b64encode(os.urandom(32)),
                    oauth_signature="",
                    oauth_signature_method="HMAC-SHA1",
                    oauth_timestamp=int(time.time()),
                    oauth_token=access_token,
                    oauth_version="1.0"),
    }
    r = requests.post(search_url, headers=headers)
    print r.text