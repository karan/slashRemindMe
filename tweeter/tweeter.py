#!/usr/bin/env python

# Built-in imports
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
USERNAME = 'slashRemindMe'

# Regex to pull out the reminder message from the tweet
REMINDER_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DEFAULT_TZ = 'UTC'
DEFAULT_REMINDER_MESSAGE = 'This is your set reminder for %s UTC'  # timestamp

AFTER_TWEET_SLEEP = 2
SLEEP = 2 * 60

logging.basicConfig(filename='logger.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connect to the db
db = dataset.connect(DATABASE_URL)
print('DATABASE_URL=%s' % DATABASE_URL)
table = db['reminders']

# Twitter client
auth = tweepy.OAuthHandler(TWITTER_KEY, TWITTER_SECRET)
auth.set_access_token(TWITTER_TOKEN, TWITTER_TOKEN_SECRET)
api = tweepy.API(auth)

# parsedatetime object
cal = pdt.Calendar()


def now():
    """Get the current time in UTC."""
    ts = cal.parse('now', datetime.now(timezone(DEFAULT_TZ)))[0]
    return time.strftime(REMINDER_TIME_FORMAT, ts)


def search_db():
    '''Returns a list of all rows from db that we can remind right now.'''
    now_ts = now()
    result = db.query(('select * from reminders '
                       'where sent_tweet_id = \'\''
                       'and reminder_time::timestamp < \'%s\'::timestamp;' % now_ts))

    logging.info('search_db: %d results for time %s' % (
                result.count, now_ts))
    return result


def send_reminders(result):

    for r in result:
        r = dict(r)
        reminder_message = '@%s %s'  # username, message
        if not r['reminder_message']:
            reminder_message = reminder_message % (r['username'], DEFAULT_REMINDER_MESSAGE % r['reminder_time'])
        else:
            reminder_message = reminder_message % (r['username'], r['reminder_message'])

        logging.info('send_reminders: id=%s, reminder_time=%s' % (r['id'], r['reminder_time']))
        try:
            parent = r['parent_tweet_id'] or r['tweet_id']
            sent_status = api.update_status(status=reminder_message,
                in_reply_to_status_id=parent)

            table.update({
                'id': r['id'],
                'sent_ts': now(),
                'sent_tweet_id': sent_status.id_str },
                ['id'])
            logging.info('send_reminders: %s sent %s' % (sent_status.text, sent_status.id_str))
        except tweepy.TweepError as e:
            logging.error('send_reminders: %s' % (e))

        time.sleep(AFTER_TWEET_SLEEP)


if __name__ == '__main__':
    print('Tweeter started...')
    while True:
        if len(db['reminders']) > 0:
            # Search database for entries with reminder_time <= now and sent_tweet_id == ''
            result = search_db()
            # Send the reminder
            send_reminders(result)

        logger.info('sleeping...')
        time.sleep(SLEEP)
