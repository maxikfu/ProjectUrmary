import vk
import requests
import datetime as dt_today
from OperationWithMembers import *
from datetime import datetime


# Post Bday wishes once a day at 9 am MSK using as a picture profile picture if set,
# otherwise using template

class MemberBirthDay:
    def get_memebers_birth_days(self, auth, p_count):
        # not getting all the users, there are the limit
        # response = api.groups.getMembers(group_id=str(auth.community_id * (-1)), fields=additional_fields)
        operation = OperationWithMembers()
        additional_fields = ['sex', 'bdate', 'can_write_private_message', 'photo_max_orig']
        members = operation.get_all_members(auth.community_id*(-1), additional_fields)
        # print(members)
        for member in members:  # searching for the bDays
            # if p_count > 25:  # limit bday wishes
            #     break
            if 'bdate' in member:  # bDay is not hidden
                today_day = str(dt_today.date.today().day)
                today_month = str(dt_today.date.today().month)
                member_bdate = member['bdate'].split('.')
                if (today_day == member_bdate[0]) and (today_month == member_bdate[1]):
                    # api.messages.send(peer_id=member['id'], message=birthday_template)
                    # switching to user access token to use wall.post
                    sessions = vk.Session(access_token=auth.user_token)
                    api = vk.API(sessions, v='5.78')

                    birthday_template = member['first_name'] + ' ' + member['last_name']+' '\
                                        +'Поздравляем тебя с днём рождения 🎉🎊🎉 \n ' \
                                         'Всего самого наилучшего) Дарим тебе лайки) 💜💛💚💙💖'

                    # getting all profile pictures chronological order
                    all_profile_pictures = api.photos.get(owner_id=member['id'], album_id='profile', rev=1)

                    # checking if member has profile picture at this moment
                    if all_profile_pictures['items'] and \
                            str(member['photo_max_orig']) != 'https://vk.com/images/camera_400.png?ava=1':
                        ava = all_profile_pictures['items'][0]
                        att_photo = 'photo' + str(ava['owner_id']) + "_" + str(ava['id'])
                    else:
                        att_photo = 'photo491551942_456239054'

                    # posting to wall
                    api.wall.post(owner_id=auth.community_id, from_group=1, signed=0,
                                  message=birthday_template, attachments=att_photo)
                    p_count += 1
        return p_count
