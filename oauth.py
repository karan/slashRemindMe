import config
import os
import webbrowser

import tweepy


"""
    Query the user for their consumer key/secret
    then attempt to fetch a valid access token.
"""
if __name__ == "__main__":

    consumer_key = os.environ.get('TWITTER_KEY', '')
    consumer_secret = os.environ.get('TWITTER_SECRET', '')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # Open authorization URL in browser
    webbrowser.open(auth.get_authorization_url())

    # Ask user for verifier pin
    pin = raw_input('Verification pin number from twitter.com: ').strip()

    # Get access token
    token = auth.get_access_token(verifier=pin)

    # Give user the access token
    print 'Access token: '
    print token
