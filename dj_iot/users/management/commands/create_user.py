from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username')
        parser.add_argument('--mail', type=str, help='User Email')
        parser.add_argument('--pw', type=str, help='User Password')

    def handle(self, *args, **kwargs):
        user = kwargs['user']
        mail = kwargs['mail']
        pw = kwargs['pw']
        User.objects.create_user(username=user, email=mail, password=pw)
