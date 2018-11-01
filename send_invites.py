from OperationWithMembers import *
import time
import ast
import datetime
import random

# -69206490  urmary online
operation = OperationWithMembers()

auth = Auth('tokens.txt')
sessions = vk.Session(access_token=auth.user_token)
api = vk.API(sessions, v='5.78')
fields = ['sex', 'bdate', 'can_write_private_message', 'can_post']
all_members = operation.get_all_members(-69206490*(-1), fields)


with open('sent_invites.txt', 'r') as f:
    invite = f.read()
if invite:
    invite_sent = ast.literal_eval(invite)
else:
    invite_sent = []
message_temp = 'Добрый день. \n Вы получили данное сообщение так как состоите в группе Урмары Online | ' \
               'Главный Урмарский Паблик. Мы просим Вас протестировать аналог этого паблика ' \
               '  https://vk.com/projecturmary' \
               '  где нет задержек новостей, поздравления с Днем Рождения и новый контент публикуется регулярно,' \
               ' так как управление пабликом осуществляется за счет бота (пргораммы) круглосуточно. ' \
               'Если Вам будет интересен контент не забудьте подписаться. \n Так же у вас есть ' \
               'возможность пообщаться с чат ботом первого поколения - Элиза.' \
               ' Для этого отправьте слово Элиза в личку паблика  \n' \
               'Спасибо за уделенное время.'
message_temp2 = 'you will like it https://vk.com/projecturmary'

count = 0
fatal_error = 0
error = False
random.shuffle(all_members)
# for m in all_members:
#     if m['id'] == 62741610:
#         all_members = [m]
#         break
for member in all_members:
    # if m['id'] == 54872678:
    #     member = member

    if count == 19:
        break
    if member['id'] not in invite_sent:
        error = False
        time.sleep(5)
        if member['can_write_private_message'] == 1:
            #try:
            print(member)
            api.messages.send(peer_id=member['id'], message=message_temp, attachment='photo491551942_456239067')
            invite_sent.append(member['id'])
            count += 1
            #except:
            #    print('error sending private messages')
            #    error = True
            #    break
        # if error:
        #     try:
        #         api.friends.add(user_id=member['id'], text=message_temp, follow=0)
        #         #invite_sent.append(member['id'])
        #         count += 1
        #     except:
        #         print('error adding friends')
        #         fatal_error += 1
with open('sent_invites.txt', 'w') as f:
    f.write(str(invite_sent))
with open('Logs/invites.log', 'a') as f:
    # this is what going to the log file
    f.write(str(datetime.datetime.now())+' Number of invite sent =  ' + str(count))
print(count)
