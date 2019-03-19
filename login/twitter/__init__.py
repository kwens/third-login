# -*- coding: utf-8 -*-
import base64
import random
from collections import OrderedDict


def generate_nonce():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    sa = []
    for i in range(32):
        sa.append(random.choice(seed))
    s = ''.join(sa)
    salt = base64.b64encode(s.encode('utf-8')).decode()
    return salt


def qs2dict(s):
    dic = OrderedDict()
    for param in s.split('&'):
        (key, value) = param.split('=')
        dic[key] = value
    return dic


def dict2qs(dic):
    return ', '.join(['%s="%s"' % (key, value) for key, value in dic])
