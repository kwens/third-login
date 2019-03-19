# -*- coding: utf-8 -*-
import random
import hashlib

def generate_random_code(length):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    s = ''.join(sa)
    m = hashlib.md5()
    m.update(s.encode(encoding='UTF-8'))
    salt = m.hexdigest()
    return salt
