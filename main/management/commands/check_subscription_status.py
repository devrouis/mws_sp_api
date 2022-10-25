from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import AppSettings
from main.enums import *
from main.paypal_apis import get_client, list_products, list_billing_plans, create_default_product, create_default_plan

appsettings = AppSettings.load()
class Command(BaseCommand):
  def handle(self, *args, **options):
    client = get_client(appsettings.paypal_client_id, appsettings.paypal_client_secret)
    products = list_products(client)
    print(products)
    default_product = [p for p in products if p.id == PP_DEFAULT_PRODUCT_ID]
    
    if len(default_product) == 0:
      product_id = create_default_product(client)
      if not product:
        print('product not created ')
        return

    billing_plans = list_billing_plans(client)
    
    if len(billing_plans) > 0:
      print('plan already exists')
      return

    plan_id = create_default_plan(client)
    if not plan_id:
      print('plan was not created')
      return
    
    print(f'plan {plan_id} was created')

      