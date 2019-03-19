# -*- coding: utf-8 -*-
from app.utils.twitter.twitter_helper import TwitterHelper
from config import JsonConfig

if __name__ == '__main__':
    twitter_cfg = JsonConfig.get('TWITTER')
    twitter_helper = TwitterHelper(twitter_cfg.get('CONSUMER_KEY'), twitter_cfg.get('COMSUMER_KEY_SECRET'),
                                   proxy=True)
    # res_data = twitter_helper.get_request_token(twitter_cfg.get('CALLBACK_URL'))
    # print('res_data', res_data)

    oauth_token = 'MHPwawAAAAAA8c5SAAABZ7o_OGo'
    oauth_secret = '6RQOpzPB8YoL99oLe3jajjwdVv54bqrX'
    oauth_verify = 'vxUis2ayc0vZxaJlrAaXobqFgGgJsz9p'
    ac_data = twitter_helper.get_access_token(oauth_token=oauth_token, oauth_token_secret=oauth_secret, oauth_verifier=oauth_verify)
    print('ac_data', ac_data)
    ac_token = ac_data.get('oauth_token')
    ac_secret = ac_data.get('oauth_token_secret')
    p_data = twitter_helper.update_status(oauth_token=ac_token, oauth_token_secret=ac_secret)
    print(p_data)
