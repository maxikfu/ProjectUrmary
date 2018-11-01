import requests
from bs4 import BeautifulSoup
from Auth import *
import vk
import json
import os
import sys
from RePost import *
import random
import datetime


class WebScraping:

    def news_scraping(self, site_url):
        # getting page content
        page = requests.get(site_url)

        posts = RePost()
        # parsing html
        soup = BeautifulSoup(page.content, 'html.parser')

        # looking for the news list
        div_container = soup.find('div', attrs={'id': 'ContetntBlock'})
        news_container = div_container.find('div', attrs={'class': 'CntentBlock'})
        news_list_all = news_container.find_all('div', attrs={'class': 'ListItem'})
        posts_made = 0
        with open('Storage/old_news.txt', 'r') as f:
            result = f.read()
            dict_old_news = json.loads(result)
        new_off_news = []
        for news_list in reversed(news_list_all):  # looping through all news to post all or only new ones backwards
            a_tag = news_list.find('a', attrs={'class': 'LI_Imege'})
            details = news_list.find('a', attrs={'class': 'LI_Details'})
            start_id = details['href'].find('id=') + 3
            end_id = details['href'].find('&')
            article_id = details['href'][start_id:end_id]
            if article_id not in dict_old_news['off_website']:
                if a_tag:
                    image_url = 'http://urmary.cap.ru/' + a_tag.find('img')['src']
                else:  # no image
                    image_url = False

                full_article_url ='http://urmary.cap.ru/' + details['href']

                # getting full article text
                full_article_page = requests.get(full_article_url)
                soup = BeautifulSoup(full_article_page.content, 'html.parser')
                div_container = soup.find('div', attrs={'id': 'ContetntBlock'})

                title = div_container.find('h1').text.strip().replace('Новости » ', '')
                title = title.replace('Объявления »', 'ОБЪЯВЛЕНИЕ »')
                news_container = div_container.find('div', attrs={'class': 'CntentBlock'})
                paragraph_container = news_container.find('div', attrs={'id': 'ContentBody_DivRec'})
                p_tags = paragraph_container.find_all('p', attrs={'style': ['text-align: justify;',
                                                                            'margin: 0cm; margin-bottom: .'
                                                                            '0001pt; text-align: justify; '
                                                                            'line-height: 150%; background: white;']})

                article_text = ''
                for tags in p_tags:
                    article_text = article_text + tags.text + '\n'
                auth = Auth('tokens.txt')
                sessions = vk.Session(access_token=auth.user_token)
                api = vk.API(sessions, v='5.78')
                try:
                    # making post here
                    # getting server destination where we are going to upload photo on the wall
                    # IMPORTANT: group_id positive!!!!!
                    if image_url:
                        destination = api.photos.getWallUploadServer(group_id=auth.community_id * (-1))
                        image_get = requests.get(image_url, stream=True)
                        # converting to multipart format, name of image doesn't metter
                        data = ("image.jpg", image_get.raw, image_get.headers['Content-Type'])
                        # sending files to server and getting photo id, owner_id etc
                        meta = requests.post(destination['upload_url'], files={'photo': data}).json()
                        photo = api.photos.saveWallPhoto(group_id=auth.community_id * (-1), photo=meta['photo'],
                                                         server=meta['server'], hash=meta['hash'])
                        # attachment need to be in special format
                        att_photo = 'photo' + str(photo[0]['owner_id']) + "_" + str(photo[0]['id'])
                    else:
                        att_photo = None
                    mess_template = title + '\n \n' + article_text + '\n Первоисточник: http://urmary.cap.ru/'

                    # posting to wall
                    api.wall.post(owner_id=auth.community_id, from_group=1, signed=0,
                                  message=mess_template, attachments=att_photo)
                    posts_made += 1
                    posts.set_post_number(posts.get_posts_number(), 1)
                    dict_old_news['off_website'].append(article_id)
                    new_off_news.append(article_id)

                except:
                    #api.messages.send(peer_id=54872678, message='Error posting new news from off website' + title)
                    pass
            else:
                new_off_news.append(article_id)
        # save to storage id we already posted
        data = json.dumps(dict_old_news)
        with open('Storage/old_news.txt', 'w') as f:
            f.write(data)
        #with open('Logs/off_website.log', 'a') as f:
            # this is what going to the log file
            #f.write(str(datetime.datetime.now()) + ' urmary_off_site.py Made posts = ' + str(posts_made) + '\n')


pid = str(os.getpid())
pidfile = "Logs/off_website.pid"
if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
with open(pidfile, 'w') as f:
    f.write(pid)
try:
    news_url = 'http://urmary.cap.ru/Info.aspx?type=news'
    announcements_url = 'http://urmary.cap.ru/Declarations.aspx'
    off_website_news = WebScraping()
    all_urls = [news_url, announcements_url]
    random.shuffle(all_urls)
    for url in all_urls:
        off_website_news.news_scraping(url)
finally:
    os.unlink(pidfile)
