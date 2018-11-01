# ProjectUrmary
This project uses VK API to help managing community in social network vk.com. 
In this project I implemented next functionalities:
1)	Publishing anonymously or not suggested posts from community members depending on their preference
2)	Automatically posting Birthday wishes to community wall.
3)	Extracting relative news from local news web site and publish them om community wall every day. (Web scrapping)
4)	Chat bot Eliza linked to community messages with ability for users to start conversation with chat bot by using specific key words.
5)	Repost news from popular communities
6)	Sending invites to the users who are members of different communities or public pages.

All these implementation was deployed to AWS server with S3 storage and scheduled to execute via Cron jobs in a certain interval. Unfortunately, if using S3 to write and read all data free tier is not enough. So, at this moment I decided to use simple text files to store necessary data such as list of already published new, posts, invites etc.  

## Prerequisites
```
Python 3.6 with libraries (re, Beautiful Soup, NumPy, json, VK etc.)
AWS
S3 (optional)
```
You need to receive community token and user token to gain access to VK API and all functionalities (https://vk.com/dev/access_token). Save these tokens in tokens.txt file (IMPORTANT: DO NOT share this information with public).

## Authors
* **Maksim Egorov** - [Maxikfu](https://github.com/Maxikfu)