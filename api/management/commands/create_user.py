from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Creates a user with an API key if necessary and display it"

    def add_arguments(self, parser):
        parser.add_argument(
            "user",
            type=str,
            nargs="?",
            help="username of the user to create",
        )

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=options["user"] or "torznab"
        )
        if created:
            user.save()
            user.set_unusable_password()

        token, created = Token.objects.get_or_create(user=user)
        print(f"API Key: {token.key}")
