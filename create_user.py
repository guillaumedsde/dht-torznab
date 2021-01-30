#!/usr/bin/env python

import django

django.setup()

from django.contrib.auth.models import User  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402

if __name__ == "__main__":

    user, created = User.objects.get_or_create(username="torznab")
    if created:
        user.save()
        user.set_unusable_password()

    token, created = Token.objects.get_or_create(user=user)
    print(f"API Key: {token.key}")
