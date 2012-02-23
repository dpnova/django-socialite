import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.utils import get_unique_username
from socialite.apps.linkedin import models
from socialite.apps.base.signals import post_register_service

def register_service(user_info, unique_id=None, access_token=None, impersonate=None):
    # FIXME: massive race condition potential here
    unique_id = unique_id or user_info['id']

    try:
        service = models.LinkedInService.objects.get(unique_id=unique_id)
    except models.LinkedInService.DoesNotExist:
        user = User(password=hashlib.md5(str(random.random())).hexdigest())
        service = models.LinkedInService()
    else:
        user = service.user

    screen_name = ''.join((user_info['firstName'], user_info['lastName']))
    if not user.username:
        user.username = get_unique_username(screen_name)
    if not user.first_name:
        user.first_name = user_info['firstName']
    if not user.last_name:
        user.last_name = user_info['lastName']
    user.save()

    # update service
    service.user = user
    service.unique_id = unique_id
    service.screen_name = screen_name[:20]
    service.impersonated_unique_id = impersonate or ''
    service.access_token = access_token
    service.save()
    post_register_service.send(sender=models.LinkedInService, instance=service, user_info=user_info)
    return service
