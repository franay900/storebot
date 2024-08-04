from django.core.management.base import BaseCommand
from bot.main import *
import asyncio

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        asyncio.run(main())