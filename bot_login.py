import praw
import os


def bot_login():
    print("Logging in...")
    try:
        reddit = praw.Reddit(client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            username=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            user_agent="RCDBot (by u/RCDBot)")
        print("Logged in!")
    except:
        print("Failed to log in!")
    return reddit


