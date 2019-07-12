# -*- coding: utf-8 -*-
"""
Created by lzq on 2018/12/5
"""
import json

import requests

from app import generate_id
from app.utils.log.logger import logger
from config import JsonConfig


class FacebookHelper:
    proxies = {}

    def __init__(self, app_id, app_secret, proxy=False):
        # self._redirect_uri = redirect_uri
        # self._access_token = ''
        # self._expires_in = 0
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy = proxy
        self.api_ver = 'v3.2'
        self._base_url = 'https://graph.facebook.com/{0}'.format(self.api_ver)

    def request(self, params, method='get'):
        logger.info('login facebook request', tag="fb_login_request",
                    trace_id=generate_id())
        url = '{0}/{1}'.format(self._base_url, params)
        proxies = self.proxies if self.proxy else {}
        print('proxy', proxies)
        try:
            res = requests.request(method, url, proxies=proxies, timeout=30)
            print('fb request status code', res.status_code)
            print('fb request content', res.content)
            data = res.json()
            app_usage = res.headers.get("X-App-Usage")
            if app_usage:
                usage = json.loads(app_usage)
                call_count = int(usage.get("call_count"))
                if call_count >= 100:
                    return 'exceed', False
            if data.get('error'):
                return data['error'], False
            return data, True
        except Exception as e:
            print("fb request exception", url, res)
            return None, False

    def build_login_url(self, state='', redirect_uri=''):
        url = '''https://www.facebook.com/{0}/dialog/oauth?client_id={1}&redirect_uri={2}&state={3}&response_type={4}&scope={5}'''
        return url.format(self.api_ver, self.app_id, redirect_uri, state, 'code', 'email')

    def get_access_token(self, code, redirect_uri):
        """
        根据code获取token
        resp
        {
            "access_token":"sdfgdfhdthdfhgdfgdfg",
            "token_type":"bearer",
            "expires_in":5177521
        }
        :param code:
        :return:
        """
        params = 'oauth/access_token?client_id={0}&redirect_uri={1}&client_secret={2}&code={3}'
        data, ok = self.request(params.format(self.app_id, redirect_uri, self.app_secret, code))
        if ok:
            # self._access_token = data.get('access_token')
            # self._expires_in = data.get('expires_in')
            return True, data
        return False, data['message']

    def refresh_access_token(self, access_token):
        """
        获取长效token
        resp
        {
            "access_token":"12scgfsfgdgrvdrndryjrt",
            "token_type":"bearer",
            "expires_in":5177521
        }
        :return:
        """
        params = 'oauth/access_token?grant_type=fb_exchange_token&client_id={0}&client_secret={1}&fb_exchange_token={2}'
        data, ok = self.request(params.format(self.app_id, self.app_secret, access_token))
        if ok:
            # self._access_token = data.get('access_token')
            # self._expires_in = data.get('expires_in')
            return True, data
        return False, data['message']

    def debug_token(self, access_token):
        """
        token校验
        resp
        {
            "data":{
                "app_id":"338589650266396",
                "type":"USER",
                "application":"demo app",
                "data_access_expires_at":1551778257,
                "expires_at":1549180205,
                "is_valid":true,
                "issued_at":1543996205,
                "scopes":[
                    "user_friends",
                    "email",
                    "public_profile"
                ],
                "user_id":"23123123123"
            }
        }
        :return:
        """
        params = 'debug_token?input_token={0}&access_token={1}|{2}'
        data, ok = self.request(params.format(access_token, self.app_id, self.app_secret))
        return ok, data

    def get_user_data(self, access_token):
        """
        获取用户信息 注 email 需要事先申请权限
        resp
        {
            "id":"104339967271939",
            "name":"Open Graph Test User",
            "email":"open_myarftz_user@tfbnw.net"
        }
        :return:
        """
        params = 'me?fields=id,name,email&access_token={0}'
        data, ok = self.request(params.format(access_token))
        if not ok and 'message' in data:
            return ok, data['message']
        else:
            return ok, data

    def get_user_picture(self, user_name):
        """
        获取用户头像
        :param user_name:
        :return:
        """
        url = 'http://graph.facebook.com/{0}/picture?return_ssl_resources=1&redirect=false'.format(user_name)
        proxies = self.proxies if self.proxy else {}
        res = requests.request('get', url, proxies=proxies, timeout=30)
        try:
            data = res.json()
            # img_url = data.get("url")
            if data.get('error'):
                return False, data['error']
            return True, data
        except:
            return False, None

    def get_permissions(self):
        """
        权限信息
        resp
        {
            "data":[
                {
                    "permission":"user_friends",
                    "status":"granted"
                },
                {
                    "permission":"email",
                    "status":"granted"
                },
                {
                    "permission":"public_profile",
                    "status":"granted"
                }
            ]
        }
        :return:
        """
        params = 'me/permissions?access_token={0}'
        data, ok = self.request(params.format(self._access_token))
        return ok, data



