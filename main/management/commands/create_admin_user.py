from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import User, AppSettings

class Command(BaseCommand):
  def handle(self, *args, **options):
    if User.objects.count() == 0:
      email = "admin@admin.com"
      password = 'admin'
      admin = User.objects.create_superuser(email=email, password=password)
      admin.first_name = '管理者'
      admin.last_name = '管理者'
      admin.seller_id = 'A48JJSC2FGBPX'
      admin.mws_auth_token = 'amzn.mws.00b178fa-5436-2d0e-e81e-44b783e493a1'
      admin.market_place = 'A1VC38T7YXB528'
      admin.is_active = True
      admin.is_admin = True
      admin.save()
      
      appsettings = AppSettings.load()
      appsettings.aws_access_key = 'AKIAJMGLPZZQPDEP5EHA'
      appsettings.aws_secret_key = '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'
      appsettings.save()
      
    else:
      print('Admin accounts can only be initialized if no Accounts exist')
