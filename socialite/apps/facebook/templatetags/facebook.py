from django import template
from socialite.apps.facebook.helper import get_avatar

register = template.Library()


@register.simple_tag()
def facebook_avatar(size, user, user_id="me"):
    return get_avatar(access_token=user.facebookservices.all()[0].access_token, 
                      user_id=user_id, 
                      size=size)