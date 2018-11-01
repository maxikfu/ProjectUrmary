import requests
from ELIZA import *
import re
import vk
import time
import json

# receiving tokens as obj from the file
# auth = Auth('tokens.txt')
eliza = ElizaBOT()


class EventResponse:
    multiple_questions_from_user = []

    def json_to_dict(self, json_response):
        dict_response = json.loads(json_response)
        return dict_response

    # all posts anonymous, only if specify they will be not anonymous
    def anonymity_check(self, wall_post_text):  # need more sophisticated algorithm
        if re.search(r"(не *анон)|(не *от *анон)", wall_post_text, re.IGNORECASE):  # not anon
            return 1
        elif re.search(r"\b(анон)\b|\b(анонимно)\b|(аноним)", wall_post_text, re.IGNORECASE):  # anon post
            return 0
        else:
            return 1

    def update_handler(self, event, post_count, eliza_working, long_poll):
        session = vk.Session(access_token=auth.user_token)
        api = vk.API(session, v='5.78')
        # print(event)
        eliza_replied_time = None
        if event['type'] == 'wall_post_new' and post_count < 50:  # make a new post on the community page
            if event['object']['from_id'] != auth.community_id:  # need to avoid posts made by BOT
                wall_post = event['object']
                # here we are checking for anonymity
                # by default all post anonymous
                anon = self.anonymity_check(wall_post['text'])
                api.wall.post(owner_id=auth.community_id, from_group=1, signed=anon, post_id=wall_post['id'])
                post_count += 1
                if post_count == 45:  # notify that limit exceeded
                    api.wall.post(owner_id=auth.community_id, from_group=1, signed=0,
                                  message='Post limit of 50 per day increased. Wall closed till tomorrow')
        if event['type'] == 'message_new':  # received new message
            new_message = event['object']
            if re.search(r"(Stop)|(стоп)", new_message['body'], re.IGNORECASE) \
                    and new_message['user_id'] in eliza_working and len(new_message['body'].split()) == 1:
                eliza_working.remove(new_message['user_id'])
                session = vk.Session(access_token=auth.community_token)
                api = vk.API(session, v='5.78')
                message_template = 'Your chat with Eliza ended.\n If you would like to start another chat send Eliza.'
                api.messages.send(peer_id=new_message['user_id'], message=message_template)
                # need to return token to user cause more methods available through user token
                session = vk.Session(access_token=auth.user_token)
                api = vk.API(session, v='5.78')
            elif re.search(r"(Eliza)|(Элиза)|(Start)|(Начать)", new_message['body'], re.IGNORECASE)\
                    and new_message['user_id'] not in eliza_working:  # want to talk to Eliza
                # so we create inf loop for 3 min gap between messages
                session = vk.Session(access_token=auth.community_token)
                api = vk.API(session, v='5.78')
                message_template = 'Hello, I am Eliza.\n What do you want to talk about?'
                api.messages.send(peer_id=new_message['user_id'], message=message_template)
                # need to return token to user cause more methods available through user token
                session = vk.Session(access_token=auth.user_token)
                api = vk.API(session, v='5.78')
                start_time = time.time()
                posts_made = 0
                eliza_working.append(new_message['user_id'])
                while time.time() - start_time < 180:  # 3 min
                    var_ts, posts_made, eliza_replied_time = self.event_listener(long_poll, posts_made, eliza_working)
                    # print('in the loop ', var_ts)
                    if eliza_replied_time:
                        start_time = eliza_replied_time
                        long_poll['ts'] = var_ts
                post_count += posts_made
            elif new_message['user_id'] in eliza_working:
                eliza_replied_time = float(time.time())
                # changing token to community so message will be sent from community
                session = vk.Session(access_token=auth.community_token)
                api = vk.API(session, v='5.78')
                message_template = eliza.response(new_message['body'])
                api.messages.send(peer_id=new_message['user_id'], message=message_template)
                # need to return token to user cause more methods available through user token
                session = vk.Session(access_token=auth.user_token)
                api = vk.API(session, v='5.78')
            else:
                if new_message['user_id'] not in self.multiple_questions_from_user:
                    self.multiple_questions_from_user.append(new_message['user_id'])
                    session = vk.Session(access_token=auth.community_token)
                    api = vk.API(session, v='5.78')
                    message_template = "Спасибо за Ваше сообщение, мы свяжемся с Вами в скором времени. \n Чтобы " \
                                       "пообщаться с ботом Элиза, отправьте слово 'Eliza' или вы так же " \
                                       "можете воспользоваться встроенной кнопкой в меню чата."
                    api.messages.send(peer_id=new_message['user_id'], message=message_template)
                    # straight to me
                    api.messages.send(peer_id=54872678, message='For Admin: \n' + new_message['body'])
                    # need to return token to user cause more methods available through user token
                    session = vk.Session(access_token=auth.user_token)
                    api = vk.API(session, v='5.78')
        return post_count, eliza_replied_time, long_poll['ts']

    def updates_handler(self, response_dict, p_count, eliza_working, long_poll):
        post_count = 0
        for event in response_dict['updates']:
            post_count, eliza_replied, new_ts = self.update_handler(event, p_count, eliza_working, long_poll)
        self.multiple_questions_from_user = []
        return post_count, eliza_replied, new_ts

    def event_listener(self, init_long_poll, p_count, eliza_working):
        response = requests.get(init_long_poll['server'] + '?act=a_check&key=' + init_long_poll['key'] + '&ts=' +
                                str(init_long_poll['ts']) + '&wait=25')
        # print(response.text)
        try:
            dict_response = self.json_to_dict(response.text)
        except:  # could not convert. something wrong with the post
            error = 'could not convert. something wrong with the post'
            print(error)
        if dict_response["updates"]:
            init_ts = dict_response['ts']  # need to save outside for case if code will fail
            init_long_poll['ts'] = dict_response['ts']
            p_count, last_eliza, new_ts = self.updates_handler(dict_response, p_count, eliza_working, init_long_poll)
            if new_ts:
                init_ts = new_ts
        else:
            init_ts = init_long_poll['ts']
            last_eliza = None
        return init_ts, p_count, last_eliza
