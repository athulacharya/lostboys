#!/usr/bin/python

import httplib2
import gmail
from gmail import get_credentials, create_message, send_message, query_msgs, get_message, mark_message_read
from apiclient import discovery

import tweepy
import time
import ast
import json
import os

from settings import *
from twitter_auth import *

APPLICATION_NAME = "lostboys"

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

def get_all_followers(api, user):
    all_followers = []

    for followers in limit_handled(tweepy.Cursor(api.followers_ids, id=user.id).pages()):
        all_followers += followers

    return all_followers

def user_url(username):
        return "https://twitter.com/" + username

def main():
    # setup gmail API
    credentials = get_credentials(CLIENT_SECRET_FILE, SCOPES, APPLICATION_NAME)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # set up twitter API
    # set these variables up in twitter_auth.py
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # open followers file, or else create empty list
    home_dir = os.path.expanduser('~')
    followers_file = os.path.join(home_dir, ".followers.json")
    try:
        with open(followers_file, 'r') as f:
            old_followers = json.load(f)
    except FileNotFoundError:
        old_followers = []

    # get user's followers
    user = api.get_user(ACCOUNT)
    followers = get_all_followers(api, user)

    # compare lists and populate lost followers
    lost_followers = []
    for old_follower in old_followers:
        if(not old_follower in followers):
            lost_followers += [old_follower]

    # get the full user data structure for each lost follower, if the follower's account still exists
    lost_boys = []
    very_lost_ids = []  # for IDs that return a user that doesn't exist
    for lost_follower in lost_followers:
        try:
            lost_boy = api.get_user(lost_follower)
            lost_boys += [lost_boy]
        except tweepy.error.TweepError as err:
            if err.api_code == 63 or err.code == 50:
                very_lost_ids += [lost_follower]
            else:
                print("Error: " + err.response.text + " (" + err.api_code + ")\n")

    # if you lost followers, send you an email about it
    if len(lost_boys) > 0 or len(very_lost_ids) > 0:
        # construct email
        body = "You have lost the following users: \n"
        for lost_boy in lost_boys:
            body += user_url(lost_boy.screen_name) + "\n"

        if very_lost_ids != []:
            body += "You also lost these IDs that I can't match up to a username: \n"
            for lost_follower in very_lost_ids:
                body += lost_follower + "\n"

        # send email
        message = create_message(SENDER, RECEIVER, "You lost some followers :(", body)
        send_message(service, "me", message)

    # write current followers to file
    with open(followers_file, 'w') as f:
            json.dump(followers, f, sort_keys=True)
            


if __name__ == '__main__':
    main()

