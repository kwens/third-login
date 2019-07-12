# coding:utf-8
import json

import requests


class DingDingApi(object):
    def __init__(self, corp_id: str = '', corp_secret: str = ''):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.host = 'https://oapi.dingtalk.com'
        self.access_token = ''

    @property
    def get_access_token(self):
        """
        获取access_token
        """
        try:
            access_url = '{0}/gettoken?corpid={1}&corpsecret={2}'.format(self.host, self.corp_id, self.corp_secret)
            r = requests.get(access_url)
            res = r.text
            res = json.loads(res)
            if res.get("errcode") == 0:
                print('access_token', res)
                self.access_token = res.get('access_token')
                return res.get('access_token')
            else:
                print(res.get("errcode"), "获取微信token失败，异常信息：" + res.get("errmsg", ''))
        except requests.exceptions.ConnectionError:
            print(1, 'ConnectionError')

    def get_user(self, access_token, code):
        try:
            get_user_url = '{0}/user/getuserinfo?access_token={1}&code={2}'.format(self.host, access_token, code)
            r = requests.get(get_user_url)
            res = r.text
            res = json.loads(res)
            if res.get("errcode") == 0:
                print('user_info', res)
            else:
                print(res.get("errcode"), "获取微信token失败，异常信息：" + res.get("errmsg", ''))
        except requests.exceptions.ConnectionError:
            print(1, 'ConnectionError')

    def get_user_info(self, user_id):
        try:
            get_user_url = '{0}/user/get?access_token={1}&userid={2}'.format(self.host, self.access_token, user_id)
            r = requests.get(get_user_url)
            res = r.text
            res = json.loads(res)
            if res.get("errcode") == 0:
                print('user_info', res)
            else:
                print(res.get("errcode"), "获取微信token失败，异常信息：" + res.get("errmsg", ''))
        except requests.exceptions.ConnectionError:
            print(1, 'ConnectionError')

    def get_depart(self, access_token):
        try:
            get_depart_url = '{0}/department/list?access_token={0}'.format(self.host, access_token)
            r = requests.get(get_depart_url)
            res = r.text
            res = json.loads(res)
            if res.get("errcode") == 0:
                print('department', res)
            else:
                print(res.get("errcode"), "获取部门列表失败，异常信息：" + res.get("errmsg", ''))
        except requests.exceptions.ConnectionError:
            print(1, 'ConnectionError')

    def get_depart_user_list(self, access_token, dept_id):
        try:
            get_url = '{0}/user/simplelist?access_token={0}&department_id={2}'.format(self.host, access_token, dept_id)
            r = requests.get(get_url)
            res = r.text
            res = json.loads(res)
            if res.get("errcode") == 0:
                print('userlist', res)
            else:
                print(res.get("errcode"), "获取用户列表失败，异常信息：" + res.get("errmsg", ''))
        except requests.exceptions.ConnectionError:
            print(1, 'ConnectionError')
