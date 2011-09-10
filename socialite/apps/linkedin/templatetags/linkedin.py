from django import template
from socialite.apps.linkedin.helper import get_avatar

register = template.Library()


@register.simple_tag()
def linkedin_avatar(user, user_id=None):
    return get_avatar(access_token=user.linkedinservices.all()[0].access_token, user_id=user_id)