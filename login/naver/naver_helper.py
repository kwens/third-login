# -*- coding: utf-8 -*-
"""
Created by cyy on 2019/1/8
"""
import requests

from config import JsonConfig

NAVER_OAUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USER_URL = "https://openapi.naver.com/v1/nid/me"
NAVER_VERIFY_TOKEN_URL = "https://openapi.naver.com/v1/nid/verify"

class NaverHelper:
    # proxies = {
    #     'https': 'http://proxy.dianchu.cc:7777'
    # }
    proxies = JsonConfig.get("PROXIES")

    def __init__(self, app_id, app_secret, proxy=False):
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy = proxy

    def build_login_url(self, state, redirect_uri=''):
        url = '''{0}?client_id={1}&redirect_uri={2}&state={3}&response_type={4}'''
        return url.format(NAVER_OAUTH_URL, self.app_id, redirect_uri, state, 'code')

    def request(self, url, data={}, header={}, method='get'):
        proxies = self.proxies if self.proxy else {}
        res = requests.request(method, url, data=data, headers=header, proxies=proxies, timeout=30)
        try:
            data = res.json()
            if data.get('error'):
                return data['error_description'], False
            return data, True
        except Exception as e:
            return None, False

    def get_access_token(self, state, code, redirect_url):
        """
        访问令牌请求
        :param code:
        :param state:
        :return:
        {
            "access_token": "AAAAQosjWDJieBiQZc3to9YQp6HDLvrmyKC+6+iZ3gq7qrkqf50ljZC+Lgoqrg",
            "refresh_token": "c8ceMEJisO4Se7uGisHoX0f5JEii7JnipglQipkOn5Zp3tyP7dHQoP0zNKHUq2gY",
            "token_type": "bearer",
            "expires_in": "3600"
        }
        """
        url = '''{0}?client_id={1}&client_secret={2}&grant_type={3}&state={4}&code={5}&redirect_uri={6}'''
        url = url.format(NAVER_TOKEN_URL, self.app_id, self.app_secret, 'authorization_code', state, code, redirect_url)
        data, ok = self.request(url)
        return ok, data

    def get_user_info(self, access_token):
        """
        获取用户信息
        :param access_token:
        :return:
        {
          "resultcode": "00",
          "message": "success",
          "response": {
            "email": "openapi@naver.com",
            "nickname": "OpenAPI",
            "profile_image": "https://ssl.pstatic.net/static/pwe/address/nodata_33x33.gif",
            "age": "40-49",
            "gender": "F",
            "id": "32742776",
            "name": "오픈 API",
            "birthday": "10-01"
          }
        }
        """
        url = NAVER_USER_URL
        header = "Bearer {0}".format(access_token)
        headers = {"Authorization": header}
        data, ok = self.request(url, header=headers)
        if ok:
            if data.get("resultcode") == "00":
                return ok, data.get("response")
            else:
                return False, data
        return ok, data

    def verify_token(self, token):
        """
        访问令牌验证和授权检查
        :param token:
        {
            "resultcode":"",
            "message": "",
            "responnse": {
                "token": "",
                "expire_date": "",
                "allowed_profile": "profile/id,profile/name,profile/profileimage"  # 允许的个人资料项目
            }
        }
        :return:
        """
        url = "{0}?info=true".format(NAVER_VERIFY_TOKEN_URL)
        header = "Bearer {0}".format(token)
        headers = {"Authorization": header}
        data, ok = self.request(url, header=headers)
        if ok:
            if data.get("resultcode") == "00":
                return ok, data.get("response")
            else:
                return False, data
        return ok, data

    def refresh_token(self, refresh_token):
        """
        刷新token
        :param access_token:
        :return:
        {
            "access_token": "AAAAQjbRkysCNmMdQ7kmowPrjyRNIRYKG2iGHhbGawP0xfuYwjrE2WTI3p44SNepkFXME/NlxfamcJKPmUU4dSUhz+R2CmUqnN0lGuOcbEw6iexg",
            "token_type": "bearer",
            "expires_in": "3600"
        }
        """
        url = '''{0}?client_id={1}&client_secret={2}&grant_type={3}&refresh_token={4}'''
        url.format(NAVER_TOKEN_URL, self.app_id, self.app_secret, 'refresh_token', refresh_token)
        data, ok = self.request(url)
        return ok, data
