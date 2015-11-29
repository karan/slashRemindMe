#!/usr/bin/env python

# Built-in imports
import calendar
from datetime import datetime, timedelta
import logging
import os
import re
import time

# Third-party dependencies
import dataset
import tweepy
import parsedatetime.parsedatetime as pdt
from pytz import timezone


# Set the Twitter credentials
TWITTER_KEY = os.environ.get('TWITTER_KEY', '')
TWITTER_SECRET = os.environ.get('TWITTER_SECRET', '')
TWITTER_TOKEN = os.environ.get('TWITTER_TOKEN', '')
TWITTER_TOKEN_SECRET = os.environ.get('TWITTER_TOKEN_SECRET', '')

DATABASE_URL = 'postgresql://postgres:postgres@%s:%s/' % (
    os.environ.get('POSTGRES_PORT_5432_TCP_ADDR'),
    os.environ.get('POSTGRES_PORT_5432_TCP_PORT'))


MAX_TWEET_LENGTH = 140
BACKOFF = 0.5  # Initial wait time before attempting to reconnect
MAX_BACKOFF = 300  # Maximum wait time between connection attempts
USERNAME = 'slashRemindMe'

# Regex to pull out the reminder message from the tweet
INPUT_MESSAGE_RE = '(["].{0,9000}["])'
REMINDER_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DEFAULT_TIME = '1 day'
DEFAULT_TZ = 'UTC'

# Messages
REMINDER_SET_MESSAGE = '@%s Cool. I\'ll remind you at %s UTC'  # username, time

# BLACKLIST
# Do not respond to queries by these accounts
BLACKLIST = [
    'pixelsorter',
    'Lowpolybot',
    'slashKareBear'
]


logging.basicConfig(filename='logger.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connect to the db
db = dataset.connect(DATABASE_URL)
table = db['reminders']

# Twitter client
auth = tweepy.OAuthHandler(TWITTER_KEY, TWITTER_SECRET)
auth.set_access_token(TWITTER_TOKEN, TWITTER_TOKEN_SECRET)
api = tweepy.API(auth)

# backoff time
backoff = BACKOFF

# parsedatetime object
cal = pdt.Calendar()


def now():
    """Get the current time in UTC."""
    ts = cal.parse('now', datetime.now(timezone(DEFAULT_TZ)))[0]
    return time.strftime(REMINDER_TIME_FORMAT, ts)


def parse_message(full_text):
    """Returns a string message from the tweet if present, otherwise
    a default message."""

    potential_message = re.search(INPUT_MESSAGE_RE, full_text)
    if potential_message:
        return potential_message.group()
    else:
        return ''


def normalize(utc_time_dt, utc_offset):
    """Takes the UTC datetime object, normalizes using the utc_offset,
    and returns a new time.struct_time object."""
    epoch = calendar.timegm(utc_time_dt.utctimetuple())

    # If I say "tomorrow" it's in UTC. So I want to -8hr the time
    epoch += utc_offset

    return time.gmtime(epoch)


def parse_time(full_text, utc_offset):
    """Returns a string timestamp of when the reminder should be sent.
    Timestamp is in the time zone corresponding to passed offset."""

    # Either the potential_timestamp is a duration "tomorrow/1 day" or
    # absolute time ("4pm")
    # If it's duration, use UTC timestamp
    # If it's absolute timestamp, use utc_offset
    # parseDT[1]:
    #   0 = not parsed at all
    #   1 = parsed as a C{date}
    #   2 = parsed as a C{time}
    #   3 = parsed as a C{datetime}

    potential_timestamp = re.sub(INPUT_MESSAGE_RE, '', full_text).strip()

    parsed_as = cal.parse(potential_timestamp)[1]
    normalize_for_tz = False

    if not potential_timestamp or parsed_as == 0:
        # No timestamp or unparsable timestamp ==> use defaults
        potential_timestamp = DEFAULT_TIME
    elif parsed_as == 3:
        # datetime
        normalize_for_tz = True

    # Since we cannot determine if parsed_as = (1, 2) is a duration or not,
    # we assume it is duration, and don't normalize using utc_offset
    reminder_time = cal.parseDT(potential_timestamp, datetime.now(timezone(DEFAULT_TZ)))[0]
    if normalize_for_tz:
        reminder_time = normalize(reminder_time, utc_offset)
    else:
        # Convert the datetime object to time.struct_time
        reminder_time = reminder_time.timetuple()

    # Converting time ==> YYYY/MM/DD HH/MM/SS
    return time.strftime(REMINDER_TIME_FORMAT, reminder_time)


def parse_tweet(tweet_text, utc_offset):
    """Parse the tweet text and return the reminder time and message in
    tuple."""

    full_text = tweet_text[tweet_text.index('@%s' % USERNAME) + len('@%s' % USERNAME) + 1:]

    # Look for a message
    reminder_message = parse_message(full_text)

    # Look for timestamp
    reminder_time = parse_time(full_text, utc_offset)

    logging.info('parse_tweet: %s--%s' % (reminder_time.strip(), reminder_message.strip()))
    return (reminder_time.strip(), reminder_message.strip())


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global backoff
        backoff = BACKOFF

        # Collect logging and debugging data
        tweet_id = status.id_str
        tweet_text = status.text
        tweet_from = status.user.screen_name
        parent_tweet = status.in_reply_to_status_id_str or ''
        utc_offset = status.user.utc_offset or 0

        if tweet_from != USERNAME and tweet_from not in BLACKLIST and not hasattr(status, 'retweeted_status'):
            logging.info('on_status: %s--%s--%s--%s--\"%d\"' % (
                tweet_id, tweet_text, tweet_from, parent_tweet, utc_offset))

            # Parse tweet for search term
            reminder_time, reminder_message = parse_tweet(tweet_text, utc_offset)

            logging.info('on_status_parse: %s--%s' % (
                reminder_time, reminder_message))

            table.insert({
                'created_at': now(),
                'reminder_time': reminder_time,
                'reminder_message': reminder_message,
                'parent_tweet_id': parent_tweet,
                'username': tweet_from,
                'tweet_text': tweet_text,
                'tweet_id': tweet_id,
                'sent_ts': '',
                'sent_tweet_id': ''
            })

            api.update_status(
                status=REMINDER_SET_MESSAGE % (tweet_from, reminder_time),
                in_reply_to_status_id=tweet_id)

        # DEBUG ONLY
        # for r in table:
        #     print(r)
        #     print('--------')

        return True


    def on_error(self, status_code):
        global backoff
        logging.error('on_error: %d' % status_code)

        if status_code == 420:
            backoff = backoff * 2
            logging.error('on_error: backoff %s seconds' % backoff)
            time.sleep(backoff)
            return True


if __name__ == '__main__':
    print('Streamer started...')

    stream = tweepy.Stream(auth=api.auth, listener=StreamListener())
    # try:
    stream.userstream(_with='user', replies='all')
    # except Exception as e:
    #     logging.info("stream_exception: {0}".format(e))
    #     raise e
