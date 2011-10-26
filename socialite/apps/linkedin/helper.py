from django.conf import settings
from socialite.apps.base.oauth import helper as oauth_helper
import urlparse
import urllib
from django.core.urlresolvers import reverse
from oauth2 import SignatureMethod_HMAC_SHA1
try:
    import json
except ImportError:
    import simplejson as json

api_url = "https://api.linkedin.com/v1/" 
oauth_url = "https://www.linkedin.com/uas/oauth/"

oauth_actions = {
    oauth_helper.REQUEST_TOKEN: 'requestToken',
    oauth_helper.AUTHORIZE: 'authorize',
    oauth_helper.AUTHENTICATE: 'authenticate',
    oauth_helper.ACCESS_TOKEN: 'accessToken',
}
oauth_client = oauth_helper.Client(settings.LINKEDIN_KEY, settings.LINKEDIN_SECRET, oauth_url, oauth_actions)
# this should work being passed to the above, but linked in docs conflict with themselves
#, signature_method=SignatureMethod_HMAC_SHA1())


def get_unique_id(access_token, user_id=None):
    try:
        return access_token['user_id']
    except KeyError:
        pass
    return user_info(access_token, user_id=user_id)['id']

def user_info(access_token, user_id=None):
    if user_id is None:
        url = '%s?%s' % (urlparse.urljoin(api_url, 'people/~:(id,first-name,last-name,picture-url)'),"format=json")
    else:
        url = '%s?%s' % (urlparse.urljoin(api_url, 'people/id=%s:(id,first-name,last-name,picture-url)'%user_id),"format=json")
    info = json.loads(oauth_client.request(url, access_token))
    return info
    
    
def get_avatar(access_token=None,user_id=None):
    info = user_info(access_token,user_id)
    return info['pictureUrl']
    
    
def announce(access_token, link, message, picture, title):
    url = "http://api.linkedin.com/v1/people/~/shares"
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<share>
  <comment>%s</comment>
  <content>
     <title>%s</title>
     <submitted-url>%s</submitted-url>
     <submitted-image-url>%s</submitted-image-url>
  </content>
  <visibility>
     <code>anyone</code>
  </visibility>
</share>
    """ % (message, title, link, picture)
    try:
        r,c = oauth_client.request(url, access_token=access_token, method="POST", body=xml, headers={'Content-Type':'text/xml'})
    except Exception,e:
        if "201" not in repr(e):
            raise
    return True
    
    
    
    