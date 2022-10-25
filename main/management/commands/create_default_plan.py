from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import AppSettings, PaypalSubscription
from main.enums import *
from main.paypal_apis import get_client, list_products, list_billing_plans, create_default_product, create_default_plan

appsettings = AppSettings.load()
class Command(BaseCommand):
  def handle(self, *args, **options):
    client = get_client(appsettings.paypal_client_id, appsettings.paypal_client_secret)
    subscriptions = PaypalSubscription.objects.all()
    for sub in subscriptions:
      pass