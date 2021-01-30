#!/usr/bin/env python

import django

django.setup()

from django.contrib.auth.models import User  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402

if __name__ == "__main__":

    user = User.objects.create_user("user1", None, "password")
    user.save()
    token = Token.objects.create(user=user)
    print(token.key)
