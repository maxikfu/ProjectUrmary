import vk
import datetime as dt_today
import sys
import time
from S3_operations import *

s3 = S3_integration()
class RePost:
    def get_posts_number(self):  # returns dictionary
        posts = []
        # reading current number of posts made
        # for line in open('TempStorage/post_counter.txt', 'r'):
        #     posts.append(line.split())
        posts_number_by_day = s3.get('post_counter')
        return posts_number_by_day

    def set_post_number(self, posts_number_by_day, new_number):
        today_day = dt_today.date.today().day
        today_month = dt_today.date.today().month
        today_year = dt_today.date.today().year
        spec_format = str(today_day) + '_' + str(today_month) + '_' + str(today_year)
        if spec_format in posts_number_by_day:  # we increase counter
            posts_number_by_day[spec_format] += new_number
        else:  # new day, we start counting again
            posts_number_by_day[spec_format] = new_number

        # saving back to S3
        s3.put('post_counter', posts_number_by_day)
        return posts_number_by_day[spec_format]  # returning current post number this day updated number

    def get_posts(self, auth, origin_id, only_last=None):  # returns post object for reposting
        sessions = vk.Session(access_token=auth.user_token)
        api = vk.API(sessions, v='5.78')
        wall_posts = api.wall.get(owner_id=origin_id, filter='owner', count=100)
        total = wall_posts['count']
        all_posts = []
        offset = 100
        if only_last:
            new_post = wall_posts['items'][:3]
            if 'is_pinned' in new_post[0]:
                return [new_post[1]]
            else:
                return [new_post[0]]  # returning only last one
        else:
            while offset <= total:
                time.sleep(0.5)
                wall_posts = api.wall.get(owner_id=origin_id, filter='owner', count=100)
                all_posts = all_posts + wall_posts['items']
                if wall_posts['count'] > offset:
                    offset += 100
            return all_posts  # returning all the posts

    def re_post(self, auth, post):  # origin_id negative for communities
        sessions = vk.Session(access_token=auth.user_token)
        api = vk.API(sessions, v='5.78')

        api.wall.repost(object='wall'+str(post['owner_id'])+'_'+str(post['id']),
                        group_id=auth.community_id * (-1))
        return post['id']  # last posted post so we won't repeat it next time
