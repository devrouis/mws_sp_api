from .mws import mws
from .models import AppSettings

app_settings = AppSettings.load()

def get_api(user):
  return mws.Products(
    access_key = app_settings.aws_access_key,
    secret_key = app_settings.aws_secret_key,
    account_id = user.seller_id,
    region = 'JP',
    auth_token=user.mws_auth_token
  )
def get_matching_product_for_id(api, market_place, id_list, id_type = 'ASIN'):
  return api.get_matching_product_for_id(market_place, id_type, id_list).parsed

def get_competitive_pricing_for_asin(api, market_place, asin_list):
  return api.get_competitive_pricing_for_asin(market_place, asin_list).parsed
  
def get_lowest_offer_listings_for_asin(api, market_place, asin_list):
  return api.get_lowest_offer_listings_for_asin(market_place, asin_list).parsed

def get_my_price_for_asin(api, market_place, asin_list):
  return api.get_my_price_for_asin(market_place, asin_list).parsed

def get_product_categories_for_asin(api, market_place, asin_list):
  result = []
  for asin in asin_list:
    r = api.get_product_categories_for_asin(market_place, asin).parsed
    r['ASIN'] = {'value': asin}
    result.append(r)
  return result