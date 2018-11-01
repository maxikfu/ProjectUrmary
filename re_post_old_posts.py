import vk
from RePost import *
from Auth import *
import ast
import datetime
from S3_operations import *

# receiving tokens as obj from the file
auth = Auth('tokens.txt')
# time = -25794755,
groups = ["-54555230", "-25794755"]
posts = RePost()
session = vk.Session(access_token=auth.community_token)
api = vk.API(session, v='5.78')
error = None
s3 = S3_integration()
for group_single in groups:
    try:
        all_posts = posts.get_posts(auth, group_single)

        # S3 integrated storage
        dict_storage = s3.get('dict_storage')
        if group_single not in dict_storage:
            dict_storage[group_single] = []
        already_posted = dict_storage[group_single]
        # getting new post id
        for post in all_posts:
            if post['id'] not in already_posted:
                posts.re_post(auth, post)
                dict_storage[group_single].append(post['id'])
                dict_storage['post_number'] = int(posts.set_post_number(posts.get_posts_number(), 1))
                break
        # writing to S3
        s3.put('dict_storage', dict_storage)
    except:
        error = 'Some error when reposting from time'
    # this is what going to the log file
    with open('Logs/re_post.log', 'a') as f:
        f.write(str(datetime.datetime.now()) + 're_post_old_posts.py Error = ' +
                     str(error) + ' ' + str(dict_storage['post_number']) + '\n')

