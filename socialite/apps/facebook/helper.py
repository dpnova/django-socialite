import base64
import hashlib # TODO: remove dependency on Python >= 2.5
import hmac
import urllib
import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import simplejson

from socialite.apps.base.oauth20 import helper as oauth_helper
from socialite.apps.base.oauth20.utils import get_mutable_query_dict

import models

api_url = 'https://graph.facebook.com/'
oauth_url = 'https://graph.facebook.com/oauth/'
oauth_client = oauth_helper.Client(settings.FACEBOOK_APPLICATION_ID, settings.FACEBOOK_SECRET, oauth_url)

def signed(view):
    '''Based on http://developers.facebook.com/docs/authentication/canvas'''
    def _view(request, *args, **kwargs):
        signed_request = request.GET.get('signed_request', '').encode('utf-8')
        try:
            encoded_sig, payload = signed_request.split('.', 2)
        except ValueError:
            raise AttributeError("Invalid signed_request.")

        def add_padding(s):
            return '%s%s' % (s, '=' * (4 - len(s) % 4))

        sig = base64.urlsafe_b64decode(add_padding(encoded_sig))
        data = simplejson.loads(base64.urlsafe_b64decode(add_padding(payload)))

        if data['algorithm'].upper() != 'HMAC-SHA256':
            raise ValueError('Unknown algorithm. Expected HMAC-SHA256')
        expected_sig = hmac.new(settings.FACEBOOK_SECRET, payload, hashlib.sha256).digest()
        if sig != expected_sig:
            raise ValueError('Bad Signed JSON signature!')
        return view(request, data, *args, **kwargs)
    return _view


import hashlib
def users_info(access_token, ids):
    CACHE_KEY = 'facebook:users_info:%s:%s' % (access_token, hashlib.md5(str(','.join([str(i) for i in ids]))).hexdigest())
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = api_url
        fields = [
            'id',
            'name',
            'picture',
        ]
        params = {
            'ids': ','.join([str(i) for i in ids],),
            'fields': ','.join(fields),
        }
        r,c = oauth_client.request(base_uri, access_token=access_token, params=params)
        # TODO: handle response != 200
        info = simplejson.loads(c).values()
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def user_info(access_token):
    CACHE_KEY = 'facebook:user_info:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = urlparse.urljoin(api_url, 'me')
        fields = [
            'id',
            'first_name',
            'last_name',
            'name',
            'picture',
        ]
        params = {
            'fields': ','.join(fields),
        }
        r,c = oauth_client.request(base_uri, access_token=access_token, params=params)
        # TODO: handle response != 200
        info = simplejson.loads(c)
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_unique_id(access_token):
    info = user_info(access_token)
    return info['id']

def get_friend_ids(access_token):
    CACHE_KEY = 'facebook:get_friend_ids:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = urlparse.urljoin(api_url, 'me/friends')
        r,c = oauth_client.request(base_uri, access_token=access_token)
        # TODO: handle response != 200
        friends = simplejson.loads(c)
        info = [f['id'] for f in friends['data']]
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_friend_info(access_token):
    CACHE_KEY = 'facebook:get_friend_info:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = urlparse.urljoin(api_url, 'me/friends')
        fields = [
            'id',
            'first_name',
            'last_name',
            'name',
            'picture',
        ]
        params = {
            'fields': ','.join(fields),
        }
        r,c = oauth_client.request(base_uri, access_token=access_token, params=params)
        # TODO: handle response != 200
        friends = simplejson.loads(c)
        info = friends['data']
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def find_friends(access_token):
    facebook_ids = get_friend_ids(access_token)
    friends = []
    if facebook_ids:
        friends = models.FacebookService.objects.filter(unique_id__in=facebook_ids)
    return friends

def announce(access_token, message, user_id="me"):
    base_uri = urlparse.urljoin(api_url, '%s/feed' % user_id)
    q = get_mutable_query_dict({
        'access_token': access_token,
        'message': message,
    })
    r,c = oauth_client.request(base_uri, access_token=access_token, method="POST", body=q.urlencode())
    # TODO: handle response != 200
    return simplejson.loads(c)


def link(access_token, link, message=None,picture=None, user_id="me"):
    base_uri = urlparse.urljoin(api_url, '%s/feed' % user_id)
    q = {
        'access_token': access_token,
        'message': message,
        'link':link
    }
    if picture:
        q['picture'] = picture
    q = get_mutable_query_dict(q)
    r,c = oauth_client.request(base_uri, access_token=access_token, method="POST", body=q.urlencode())
    # TODO: handle response != 200
    return simplejson.loads(c)

FACEBOOK_IMAGE_SIZES = set(['square','small','normal','large'])
def get_avatar(access_token, user_id="me", size="large"):
    if size not in FACEBOOK_IMAGE_SIZES:
        raise ValueError("size must be one of %s" % FACEBOOK_IMAGE_SIZES)
    base_uri = urlparse.urljoin(api_url, '%s/picture' % (user_id,))
    """
    The following is here because oauth.client.request tries to fetch the image
    which seems to block. Instead we just return the url.
    """
    params = {'type':size}
    params['oauth_token'] = access_token
    uri = '%s?%s' % (base_uri, urllib.urlencode(params))
    return uri
