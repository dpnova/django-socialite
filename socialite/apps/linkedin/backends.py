import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.backends import BaseOauthBackend
from socialite.apps.base.oauth20.utils import get_unique_username
from socialite.apps.linkedin import helper, models
from socialite.apps.linkedin.registration import register_service

class LinkedInBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.base_url

    def get_existing_user(self, access_token):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.LinkedInService.objects.get(unique_id=unique_id)
        except models.LinkedInService.DoesNotExist:
            return None
        return service.user

    def register_user(self, access_token, impersonate=None):
        try:
            user_info = helper.user_info(access_token)
        except: # TODO: bare except, bad!
            import traceback;traceback.print_exc()
            return None 


        return register_service(user_info, unique_id=user_info['id'],
            access_token=access_token, impersonate=impersonate).user