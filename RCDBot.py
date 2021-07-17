import bot_login
import requests
import time
from requests_html import HTMLSession
from urllib.parse import quote_plus
from park_abbr_dict import park_abbr as parks

REPLY_TEMPLATE = "[{} ]({})\n\n"


def run_bot(reddit):
    """ Search the comments for keyword.

    :param reddit: instance of the bot
    :return: None
    """
    rcdb_query_list = []
    post_dict = {}
    rcdb_query_link_list = []

    # phrase to trigger the bot
    trigger_phrase = "u/RCDBot"

    print("logged in and searching comments ...")

    # check every comment in the subreddit
    for comment in reddit.subreddit("rollercoasters").stream.comments(skip_existing=True):

        # check the trigger_phrase in each comment
        if trigger_phrase in comment.body:
            triggered(comment, rcdb_query_list)
            search_rcdb(rcdb_query_list, post_dict, rcdb_query_link_list)
            reply(post_dict, comment)


def triggered(comment, rcdb_query_list):
    """ Parse the comment and extract search words/phrases.

    :param comment: PRAW comment
    :param rcdb_query_list: empty list of queries to be searched on RCDB
    :return: None
    """

    # get submission title
    post = comment.submission
    submission_title = post.title

    # set index list of special characters
    idx_list = [0, 0, 0]

    # get indices of brackets
    open_bracket_list = [i for i, letter in enumerate(submission_title) if letter == '[']
    closed_bracket_list = [i for i, letter in enumerate(submission_title) if letter == ']']

    # parse content within each pair of indices
    for i, k in zip(open_bracket_list, closed_bracket_list):
        submission_title_slice = submission_title[i + 1:k]

        # split terms if necessary
        while '@' in submission_title_slice or ',' in submission_title_slice or ' and ' in submission_title_slice:

            idx_list[0] = submission_title_slice.find('@')
            idx_list[1] = submission_title_slice.find(',')
            idx_list[2] = submission_title_slice.find(' and ')

            max_idx = max(idx_list)

            if max_idx > 0:
                if idx_list[2] == max_idx:
                    num_char_erase = 5
                else:
                    num_char_erase = 1
                rcdb_query_list.append(submission_title_slice[max_idx + num_char_erase:].strip())
                removed_from_string = submission_title_slice[:max_idx]
                submission_title_slice = removed_from_string
        # load up the query list
        rcdb_query_list.append(submission_title_slice.strip())


def search_rcdb(rcdb_query_list, post_dict, rcdb_query_link_list):
    """ Search RCDB.com for parsed terms.

    :param rcdb_query_list: list of terms to search for
    :param post_dict: dictionary of words/terms and their respective HTML queries
    :param rcdb_query_link_list: HTML query for each term
    :return: None
    """
    rcdb_addr = "https://rcdb.com/qs.htm?qs="

    # perform a search on RCDB.com
    for x in range(len(rcdb_query_list)):
        if rcdb_query_list[x].upper() in parks.keys():
            rcdb_query_list[x] = parks[rcdb_query_list[x].upper()]
        rcdb_query_link_list.append(rcdb_addr + quote_plus(rcdb_query_list[x]))
        try:
            session = HTMLSession()
            response = session.get(rcdb_query_link_list[x])
        except requests.exceptions.RequestException as e:
            print(e)
        if "Sorry" in response.html.find('p', first=True).text:
            print("sorry couldn't find {}".format(rcdb_query_list[x]))
        else:
            post_dict[rcdb_query_list[x]] = rcdb_query_link_list[x]


def reply(post_dict, comment):
    """ Post a reddit reply.

    :param post_dict: dictionary of words/terms and their respective HTML queries
    :param comment: PRAW comment to be replied to
    :return: None
    """
    # initialize the reply text
    reply_text = "\n\n"

    if post_dict:
        for key, value in post_dict.items():
            reply_text += REPLY_TEMPLATE.format(key, value)

        reply_text += "\n\n\n----\n\n>I am a bot. Beep, boop\n\n\n\n"
        print(reply_text)

        # comment the similar words
        comment.reply(reply_text)
        print("I replied to {}".format(comment.body))
    else:
        print("Couln't find anything to link to")


if __name__ == "__main__":
    while True:
        try:
            r = bot_login.bot_login()
            run_bot(r)
            time.sleep(300)

        except Exception as e:
            print(str(e.__class__.__name__) + ": " + str(e))
