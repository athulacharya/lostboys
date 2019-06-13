# lostboys
A service to email you when you lose Twitter followers.

## Overview
When executed, lostboys will download your list of followers, compare it to the list it downloaded last time, and let you know if you lost anyone.

## Installation
NOTE: This project is very much in an alpha stage! And it will likely stay that way. 

1. Clone the repo.
2. Modify the variables in settings.py.
3. Populate twitter\_auth.py. [This page](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html) has useful information.
3. Set up the GMail API as described [here](https://developers.google.com/gmail/api/quickstart/python) and save client\_secrets.json to the lostboys working directory.
4. Run lostboys.py once to authorize it to send and read emails in the sending gmail account, and also populate your list of followers.
5. Add lostboys.py to your crontab. You may want to set the HOME variable appropriately. E.g.:
  * ```30 22 * * * user HOME=/home/user /home/user/lostboys/lostboys.py >> /home/user/lostboys/log 2>&1```
  * This will run the script at 10:30 PM every day.


## Dependencies
(All of these can be installed with pip.)
* google-api-python-client
* httplib2
* oauth2client
* tweepy
