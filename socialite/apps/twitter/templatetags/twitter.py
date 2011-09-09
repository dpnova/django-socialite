from django import template

from socialite.apps.twitter import helper

register = template.Library()

@register.simple_tag()
def twitter_avatar(size, user_id):
    return helper.get_avatar(size, user_id=user_id)


@register.simple_tag()
def user_twitter_avatar(user, size):
    return helper.get_avatar(size, access_token=user.twitterservices.all()[0].access_token)