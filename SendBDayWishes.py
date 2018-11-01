# runs once a day
from MemberBirthDay import *
from RePost import *
import datetime
from S3_operations import *


session = vk.Session(access_token=auth.community_token)
api = vk.API(session, v='5.78')
getBDay = MemberBirthDay()
post_functions = RePost()
new_post_number = 0
error = None
s3 = S3_integration()
try:
    count = getBDay.get_memebers_birth_days(auth, 0)
    new_post_number = post_functions.set_post_number(post_functions.get_posts_number(), count)
except:
    error = 'Error Bday wishes sending'
# S3 integrated storage
dict_storage = s3.get('dict_storage')
dict_storage['post_number'] = int(new_post_number)
# saving new value in S3
s3.put('dict_storage', dict_storage)


with open('Logs/send_bdays.log', 'a') as f:
    # this is what going to the log file
    f.write(str(datetime.datetime.now()) + ' SendBdayWishes.py Error = ' + str(error) + ' ' + str(dict_storage['post_number']) + '\n')

