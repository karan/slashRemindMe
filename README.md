# slashRemindMe

A Twitter bot to remember things or threads.

## Table of Contents

* [About](#about)
* [Usage](#usage)
  * [Example Usage](#example-usage)
* [Time Options](#time-options)
* [FAQ](#faq)
  * [Why was the message off by a few minutes?](#why-was-the-message-off-by-a-few-minutes)
  * [Where is this bot running?](#where-is-this-bot-running)
  * [How do I see all my reminders?](#how-do-i-see-all-my-reminders)
  * [How do I delete/edit a reminder?](#how-do-i-deleteedit-a-reminder)
* [Running](#running)
* [License](#license)

## About

For example, someone tweets a playlist while you're in a meeting. Simply reply to the tread by tagging "@slashRemindMe" and a suitable time when you would like to be reminded. The reminder is sent as a tweet only to you.

Did a politician just make claims about future? `@slashRemindMe a year "to check these claims"` on the tweet, and see if they were right or not.

Think of @slashRemindMe as a "save for later" natively on Twitter. Here's some [example uses](#example-usage).

## Usage

Simply create a tweet in the format `@slashRemindMe TIME OPTION "MESSAGE" (with quotes)`.

[Time option](#time-options) and message order don't matter. They are also optional. Meaning if you can do a simple `@slashRemindMe` it will default to 1 day and a standard message. Everything before `@slashRemindMe` is not caught and everything after is.

The message will be shown in the reminder tweet.

### Example usage

* `Good claims. I'll check them later. @slashRemindMe at 4pm`
* `@slashRemindMe 16 Jan 2016 "Pres debate happening"`

## Time Options

* Bot tries to figure out your timezone. If it cannot, it defaults to PST.
* There are more options than stated here. Try to see if you can find more and I'll add them!
* EOY means end of year
* EOM means end of month
* EOD means end of day
* **BOLDED TIMES INDICATE A SET IN STONE TIME (which can cause problems if you don't live in PST)**
* It's better to use 1 day/week/month than tomorrow/next week/next month because of above

Time Option | New Time
---------|----------
RemindMe! One Year | 2015-06-01 01:37:35 PST
RemindMe! 3 Months | 2014-09-01 01:37:35 PST
RemindMe! One Week | 2014-06-08 01:37:35 PST
RemindMe! 1 Day | 2014-06-02 01:37:35 PST
RemindMe! 33 Hours | 2014-06-02 10:37:35 PST
RemindMe! 10 Minutes | 2014-06-01 01:47:35 PST
RemindMe! August 25th, 2014 | 2014-08-25 01:37:35 PST
RemindMe! 25 Aug 2014 | 2014-08-25 01:37:35 PST
RemindMe! 5pm August 25 | **2014-08-25 17:00:00 PST**
RemindMe! Next Saturday | **2014-06-14 09:00:00 PST**
RemindMe! Tomorrow | **2014-06-02 09:00:00 PST**
RemindMe! Next Thursday at 4pm | **2014-06-12 16:00:00 PST**
RemindMe! Tonight | **2014-06-01 21:00:00 PST**
RemindMe! at 4pm | **2014-06-01 16:00:00 PST**
RemindMe! 2 Hours After Noon | **2014-06-01 14:00:00 PST**
RemindMe! eoy | **2014-12-31 09:00:00 PST**
RemindMe! eom | **2014-06-30 09:00:00 PST**
RemindMe! eod | **2014-06-01 17:00:00 PST**

## FAQ

#### Why was the message off by a few minutes?

The bot currently goes to sleep every 2 minutes to save on resources. Meaning your message can be as late as 2 minutes + any connection issues it is having with Twitter.

#### Where is this bot running?

Currently I'm running this bot on a 1GB [DigitalOcean](https://www.digitalocean.com/?refcode=422889a8186d) instance (yes, that's an affiliate link. Use that to get a free VPS for 2 months). The bot is not resource-intensive and uses a couple dozen MBs of RAM.

#### How do I see all my reminders?

That is currently not possible.

#### How do I delete/edit a reminder?

That is currently not possible.

## Running

#### Requirements

- [Docker](https://docs.docker.com/installation/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Docker Machine](https://docs.docker.com/machine/install-machine/) (Mac OS X)

#### Instructions

Create a file called `config.env` that looks like `config_example.env`. Fill in the necessary values.

For Twitter config:

1. Register your app
2. Get your app's key and secret.
3. Create token and get the token and secret.

Then, to run the bot:

```bash
$ docker-compose up
```

#### Mac & Docker Machine

If you're using Docker Machine, follow these instructions for installation:

```bash
# Provision the docker engine
$ docker-machine create --driver virtualbox remindbot

# Set the environment
$ eval "$(docker-machine env remindbot)"

# See the IP address of the host
$ docker-machine ip remindbot

# Start the container
$ docker-compose up
```

## License

Apache 2.0

Strongly inspired by the [reddit bot](https://www.reddit.com/r/RemindMeBot/comments/24duzp/remindmebot_info/).
