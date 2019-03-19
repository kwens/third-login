# -*- coding: utf-8 -*-
import base64
import hmac
import json
import urllib.parse
from collections import OrderedDict
from hashlib import sha1

import requests
import time

from . import generate_nonce, dict2qs, qs2dict

try:
    from urllib import urlencode, quote
except ImportError:
    from urllib.parse import urlencode, quote

USER_REDIRECT_URL = "https://api.twitter.com/oauth/authenticate?oauth_token="
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
VERRIFY_URL = "https://api.twitter.com/1.1/account/verify_credentials.json"
SEND_TWEET_URL = "https://api.twitter.com/1.1/statuses/update.json"


class TwitterHelper:
    def __init__(self, consumer_key, comsumer_key_secret, proxy=False):
        self.consumer_key = consumer_key
        self.comsumer_key_secret = comsumer_key_secret
        self.proxy = proxy

    def get_request_token(self, callback_url):
        """
        获取request_token
        :return:
        """
        try:
            res = self.request_http('POST', REQUEST_TOKEN_URL, callback_url)
            if 'oauth_token' in res:
                oauth_data = qs2dict(res)
                oauth_callback_confirmed = oauth_data.get('oauth_callback_confirmed')
                if oauth_callback_confirmed or oauth_callback_confirmed == 'true':
                    redirect_url = '{}{}'.format(USER_REDIRECT_URL, oauth_data.get('oauth_token'))
                    oauth_data['redirect_url'] = redirect_url
                    return oauth_data
                else:
                    return {'code': -1, 'message': 'Validation failed!'}
            else:
                return self.__generate_error(res)
        except Exception as e:
            raise Exception(e)

    def get_access_token(self, oauth_token, oauth_token_secret, oauth_verifier):
        """
        获取access_token
        :return:
        """
        try:
            res = self.request_http('POST', ACCESS_TOKEN_URL, oauth_token=oauth_token,
                                    oauth_token_secret=oauth_token_secret, oauth_verifier=oauth_verifier)
            # print('access res', res)
            if 'oauth_token' in res:
                access_data = qs2dict(res)
                if 'user_id' in access_data:
                    return access_data
                else:
                    return {"code": -1, "message": 'Validation failed!'}
            else:
                return self.__generate_error(res)
        except Exception as e:
            raise Exception(e)

    def verify_credentials(self, oauth_token, oauth_token_secret):
        """
        校验用户身份（可以获取user_id和头像url）
        :param url:
        :param oauth_token:
        :param oauth_token_secret:
        :return:
        """
        try:
            res = self.request_http('GET', VERRIFY_URL, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            if 'id' in res:
                verify_data = json.loads(res)
                return verify_data
            else:
                return self.__generate_error(res)
        except Exception as e:
            raise Exception(e)

    def send_tweets(self, oauth_token, oauth_token_key, **kwargs):
        """
        发送推文（分享活动）
        :param oauth_token:
        :param oauth_token_secret:
        :return:
        """
        try:
            res = self.request_http('POST', SEND_TWEET_URL, oauth_token=oauth_token, oauth_token_secret=oauth_token_key,
                                    **kwargs)
            if 'user' in res:
                tweet_data = json.loads(res)
                return tweet_data
            else:
                return self.__generate_error(res)  # code= 187 表示已经发过
        except Exception as e:
            raise Exception(e)

    def request_http(self, http_methods, request_url, callback_url='', oauth_token='', oauth_verifier='',
                     oauth_token_secret='', **kwargs):
        """
        发送请求
        :param http_methods:       请求方式
        :param request_url:        请求地址
        :param callback_url:       回调地址
        :param oauth_token:        用户授权的token
        :param oauth_verifier:     用于校验token的值
        :param oauth_token_secret: 授权的secret
        :return:
        """
        encode_url = urllib.parse.quote(request_url, safe='', encoding='utf-8')
        params = self.__generate_params(callback_url=callback_url, oauth_token=oauth_token,
                                        oauth_verifier=oauth_verifier)
        datas = OrderedDict(params)
        if kwargs:
            datas.update(kwargs)
        oauth_signature = self.__generate_signature(http_methods, encode_url, datas,
                                                    oauth_token_secret=oauth_token_secret)
        p_encode = urllib.parse.urlencode(params)
        params = qs2dict(p_encode)
        params['oauth_signature'] = oauth_signature
        headers = self.__generate_header(params)
        res = self.__send_http(http_methods, request_url, headers, **kwargs)
        return res

    def __send_http(self, http_methods, url, headers, **kwargs):
        """
        发送请求
        :param url:     请求地址
        :param headers: 请求头
        :return:
        """
        try:
            proxies = {'https': 'http://proxy.dianchu.cc:7777'} if self.proxy else {}
            data = ''
            if kwargs:
                data = urlencode(kwargs)
                # print('data: ', data)
            if http_methods == 'POST':
                r = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=30, verify=False)
            else:
                r = requests.get(url, headers=headers, data=data, proxies=proxies, timeout=30, verify=False)
            res = r.text
        except requests.exceptions.ConnectionError as e:
            res = {"Info": "ConnectionError", "Stat": 10001, "ActionId": 0}
        except requests.exceptions.Timeout as e:
            res = {"Info": "Timeout", "Stat": 10001, "ActionId": 0}
        return res

    def __generate_header(self, auth_params):
        """
        生成请求头
        :param auth_params: 校验头参数
        :return:
        """
        p_list = [(k, auth_params[k]) for k in sorted(auth_params.keys())]
        params_header = dict2qs(p_list)
        oauth_header = 'OAuth {}'.format(params_header)
        print(oauth_header)
        print('-----------------------------------------\r\n')
        headers = dict()
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        headers['Authorization'] = oauth_header
        return headers

    def __generate_authorization(self, params):
        """
        生成验证头数据
        :param params: oauth头参数
        :return:
        """
        p_list = [(k, params[k]) for k in sorted(params.keys())]
        params_header = dict2qs(p_list)
        oauth_header = 'OAuth {}'.format(params_header)
        return oauth_header

    def __generate_params(self, callback_url='', oauth_token='', oauth_verifier=''):
        """
        生成验证头参数
        :param callback_url:
        :param oauth_token:
        :param oauth_verifier:
        :return:
        """
        timestamp = int(time.time())
        nonce = generate_nonce()
        print('timestamp', timestamp)
        print('nonce', nonce)
        print('-----------------------------------------\r\n')
        params = OrderedDict()
        if callback_url:
            params['oauth_callback'] = callback_url
        params['oauth_consumer_key'] = self.consumer_key
        params['oauth_nonce'] = nonce
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_timestamp'] = int(time.time())
        if oauth_token:
            params['oauth_token'] = oauth_token
        if oauth_verifier:
            params['oauth_verifier'] = oauth_verifier
        params['oauth_version'] = '1.0'
        return params

    def __generate_signature(self, methods, url, params, oauth_token_secret=''):
        """
        生成签名
        :param methods:            请求的方式：POST或者GET
        :param url:                请求的url
        :param params:             除了签名之外的oauth参数
        :param oauth_token_secret: 用于签名key
        :return:
        """
        # url = urllib.parse.quote(url, safe='', encoding='utf-8')
        p_encode1 = urllib.parse.urlencode(params)
        print('p_encode1', p_encode1)
        print('-----------------------------------------\r\n')
        p_encode2 = urllib.parse.quote(p_encode1)
        print('p_encode2', p_encode2)
        print('-----------------------------------------\r\n')
        signature_text = '{}&{}&{}'.format(methods, url, p_encode2)
        print('signature_text', signature_text)
        print('-----------------------------------------\r\n')

        oauth_consumer_secret = self.comsumer_key_secret
        oauth_token_secret = oauth_token_secret
        signature_key = '{}&{}'.format(oauth_consumer_secret, oauth_token_secret)

        signature = hmac.new(signature_key.encode('utf-8'), signature_text.encode('utf-8'), sha1).digest()
        signature = base64.b64encode(signature).decode()
        signature = urllib.parse.quote(signature)
        return signature

    @staticmethod
    def __generate_error(info):
        if 'errors' in info:
            error_info = json.loads(info)
            return error_info["errors"][0]
        else:
            return {"code": -2, "message": info}
