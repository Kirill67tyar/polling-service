import secrets
from django.core.management import BaseCommand

class Command(BaseCommand):
    help = u"generate SECRET_KEY for Django (the value is not saved anywhere)"

    # def add_arguments(self, parser):
    #     parser.add_argument('--days', dest='days', type=int, default=3)

    def handle(self, *args, **options):
        generated_key = secrets.token_hex(24)
        print(f'\nSECRET_KEY={generated_key}')