#!/usr/bin/python3
from MemberBirthDay import *
from EventResponse import *
from RePost import *
import datetime
import os
import sys
from S3_operations import *


pid = str(os.getpid())
pidfile = "Logs/main.pid"
if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
with open(pidfile, 'w') as f:
    f.write(pid)

try:
    error = None
    session = vk.Session(access_token=auth.user_token)
    api = vk.API(session, v='5.78')
    event_handler = EventResponse()
    getBDay = MemberBirthDay()
    posts = RePost()
    eliza_working = []
    s3 = S3_integration()
    long_poll = api.groups.getLongPollServer(group_id=auth.community_id*(-1))
    today_day = dt_today.date.today().day
    post_counter_today = 0
    already_posted = None
    # list of communities for re-posts
    daily = "-126824031"
    ted = "-50348171"
    repost_group_list = [daily, ted]

    # S3 integrated storage
    dict_storage = s3.get('dict_storage')
    if int(dict_storage['post_number']) < 48:
        try:
            for group in repost_group_list:
                # looking for the new posts from popular groups
                some_posts = posts.get_posts(auth, group, 1)
                if group in dict_storage:
                    if dict_storage[group] != some_posts[0]['id']:
                        posts.re_post(auth, some_posts[0])
                        last_post_id = some_posts[0]['id']
                        dict_storage[group] = last_post_id
                        count = 1
                        posts.set_post_number(posts.get_posts_number(), count)
                else:
                    dict_storage[group] = None
                    posts.re_post(auth, some_posts[0])
                    last_post_id = some_posts[0]['id']
                    dict_storage[group] = last_post_id
                    count = 1
                    posts.set_post_number(posts.get_posts_number(), count)
            post_limit = None
        except:
            error = 'Error while reposting, maybe reached the limit'
    else:
        post_limit = 'Reached post limit for today'
    if dict_storage['ts']:  # time start point for updates
        long_poll['ts'] = int(dict_storage['ts'])


    # sends long poll request and deals with updates
    var_ts, post_counter_today, last_eliza_run = event_handler.event_listener(long_poll, post_counter_today, eliza_working)
    # print(var_ts)
    dict_storage['ts'] = var_ts
    # writing new ts returned from event listener
    curr_post_number = posts.set_post_number(posts.get_posts_number(), post_counter_today)
    dict_storage['post_number'] = int(curr_post_number)
    s3.put('dict_storage', dict_storage)

    # with open('Logs/main.log', 'a') as f:
    #     # this is what going to the log file
    #     f.write(str(datetime.datetime.now())+' Main.py Error = ' + str(error) + ' ' + str(dict_storage['post_number']) + '\n')
finally:
    os.unlink(pidfile)



