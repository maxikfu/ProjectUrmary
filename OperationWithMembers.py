import vk
import requests
from Auth import *
import time

auth = Auth('tokens.txt')
sessions = vk.Session(access_token=auth.community_token)
api = vk.API(sessions, v='5.78')
# -69206490  urmary online
# -126824031 Daily Overview


class OperationWithMembers:
    def get_members(self, competitor_id, offset=None, fields=None):
        if fields:
            competitor_info = api.groups.getMembers(group_id=competitor_id, offset=offset, fields=fields)
        else:
            competitor_info = api.groups.getMembers(group_id=competitor_id, offset=1000)
        return competitor_info

    def get_all_members(self, competitor_id, custom_fields):
        all_members = []
        result = self.get_members(competitor_id, fields=custom_fields)
        all_members = all_members + result['items']
        total = result['count']
        offset = 1000
        while offset <= total:
            time.sleep(1)
            result = self.get_members(competitor_id, offset, custom_fields)
            all_members = all_members + result['items']
            if result['count'] > offset:
                offset += 1000
        return all_members
