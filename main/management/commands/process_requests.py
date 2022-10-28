from gettext import Catalog
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import *
from main.enums import *
from main.amazon_apis import *
import json, logging
from time import sleep
from main.mws.utils import ObjectDict
from collections import defaultdict
logger = logging.getLogger('process_requests')
appsettings = AppSettings.load()

# --SP-API--------------------------------------
from main.sp_api.sp_api_data_formatting import *
from main.sp_api.sp_asin_formatting import *
from main.sp_api.sp_api_new_formatting import *
from main.sp_api import *
from main.sp_api.sp_api_aws import *

from sp_api.base import Marketplaces
from sp_api.api import CatalogItems, CatalogItemsVersion, Products
# ------------------------------------------------

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]


def save_to_db(req, operation_name, data, asin, jan):
  logger.info(f'saving asin {asin} jan {jan}')
  try:
    p = ScrapeRequestResult.objects.get(scrape_request = req, asin = asin, jan = jan, get_matching_product_for_id_raw = data)
  except ScrapeRequestResult.DoesNotExist:
    p = ScrapeRequestResult(scrape_request = req, asin = asin, jan = jan, get_matching_product_for_id_raw = data)

  if not 'Error' in data:  
    setattr(p, f'{operation_name}_raw', json.dumps(data))
    logger.info(f'{operation_name} saved')
  p.save()

# def parse_and_save_result(req, operation_name, result_dict, asin, jan, asin_list, jan_list):
#   if req.id_type == ID_ASIN:
#     asin = result_dict['asin']
#   if 'Id' in result_dict: # for get_matching_product_for_id response
#     asin = result_dict['Id']['value']
#   if 'ASIN' in result_dict:
#     asin = result_dict['Products']['Product']['ASIN']['value']
#   asin_index = asin_list.index(asinValue)
#   save_to_db(req, operation_name, result_dict, asin, jan)

def merge_dict(d1, d2):
  dd = defaultdict(list)

  for d in (d1, d2):
      for key, value in d.items():
          if isinstance(value, list):
              dd[key].extend(value)
          else:
              dd[key].append(value)
  return dict(dd)

def product_params(list, marketplaceId, itemCondition_type):
  data = []
  for item in list:
    uri = "/products/pricing/v0/items/{}/offers".format(item)
    method = "GET"
    MarketplaceId=marketplaceId
    itemCondition = itemCondition_type
    customerType = "Consumer"

    item = {
      "uri": uri,
      "method": method,
      "MarketplaceId": MarketplaceId,
      "ItemCondition": itemCondition,
      "CustomerType": customerType
    }

    data.append(item)
  return data

def process_request(req):
  req.status = REQUEST_STATUS_IN_PROGRESS
  req.save()

  credentials=dict(
      refresh_token=req.user.sp_api_refresh_token,
      lwa_app_id=appsettings.sp_api_client_id,
      lwa_client_secret=appsettings.sp_api_client_secret,
      aws_secret_key=appsettings.sp_IAM_user_secret_key,
      aws_access_key=appsettings.sp_IAM_user_access_key,
  )
  

  MarketplaceIds=req.user.market_place
  IncludedData="attributes, dimensions, images, productTypes, salesRanks, summaries, relationships"
 
  #array convert to string
  if len(req.id_list) > 0:
    Keywords = ','.join(str(x) for x in req.id_list)
  else:
    print('There is no item list.')
  
  if req.id_type == ID_ASIN :
    if req.user.api_type == SP:
      
      
      # make body query in products pricing 
      request_by_new = product_params(req.id_list, req.user.market_place, 'New')
      request_by_used = product_params(req.id_list, req.user.market_place, 'Used')

      CatalogData = []
      NewProductsData = []
      UsedProductsData = []
      sleep(2)
      try:
        CatalogResponse = CatalogItems(credentials=credentials, marketplace=Marketplaces.JP, version=CatalogItemsVersion.V_2022_04_01).search_catalog_items(keywords=Keywords, marketplaceIds=MarketplaceIds, includedData=IncludedData)
      except Exception as e:
        print('--------catalog err:', e)
      finally:
        if CatalogResponse.errors is None:
          CatalogData = CatalogResponse.payload['items']

      sleep(2)
      try:
        NewProductsResponse = Products(marketplace=Marketplaces.JP, credentials=credentials).get_item_offers_batch(request_by_new)
      except Exception as e:
        print('--------new products err:', e)
      finally:
        if NewProductsResponse.errors is None:
          NewProductsData = NewProductsResponse.payload['responses']

      sleep(2)
      try:
        UsedProductsResponse = Products(marketplace=Marketplaces.JP, credentials=credentials).get_item_offers_batch(request_by_used)
      except Exception as e:
        print('--------used products err:', e)
      finally:
        if UsedProductsResponse.errors is None:
          UsedProductsData = UsedProductsResponse.payload['responses']

      allData = list(zip(CatalogData, NewProductsData, UsedProductsData))
      
      for item in allData:
        save_to_db(req, 'operation_name', item, 'asin', 'jan')

  elif req.id_type == ID_JAN:      
    if req.user.api_type == SP:
      print('***jan***')
      CatalogData = []
      NewProductsData = []
      UsedProductsData = []
      sleep(2)
      try:
        CatalogResponse = CatalogItems(credentials=credentials, marketplace=Marketplaces.JP, version=CatalogItemsVersion.V_2022_04_01).search_catalog_items(keywords=Keywords, marketplaceIds=MarketplaceIds, includedData=IncludedData)
      except Exception as e:
        print('--------catalog err:', e)
      finally:
        if CatalogResponse.errors is None:
          CatalogData = CatalogResponse.payload['items']
      
      asin_list = []
      for item in CatalogData:
        asin_list.append(item["asin"])

      print('asin_list')
      print(asin_list)

      if len(asin_list) > 0:
        Keywords = ','.join(str(x) for x in req.id_list)
      else:
        print('There is no item list.')

      # make body query in products pricing 
      request_by_new = product_params(asin_list, req.user.market_place, 'New')
      request_by_used = product_params(asin_list, req.user.market_place, 'Used')

      sleep(2)
      try:
        NewProductsResponse = Products(marketplace=Marketplaces.JP, credentials=credentials).get_item_offers_batch(request_by_new)
      except Exception as e:
        print('--------new products err:', e)
      finally:
        if NewProductsResponse.errors is None:
          NewProductsData = NewProductsResponse.payload['responses']

      sleep(2)
      try:
        UsedProductsResponse = Products(marketplace=Marketplaces.JP, credentials=credentials).get_item_offers_batch(request_by_used)
      except Exception as e:
        print('--------used products err:', e)
      finally:
        if UsedProductsResponse.errors is None:
          UsedProductsData = UsedProductsResponse.payload['responses']

      allData = list(zip(CatalogData, NewProductsData, UsedProductsData))
      
      for item in allData:
        save_to_db(req, 'operation_name', item, 'asin', 'jan')

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('-i', '--id', dest='id', type=int)

  def handle(self, *args, **options):
    id = options['id'] if 'id' in options else None
    logger.info(f'Started. id = {id}')
    
    requests = ScrapeRequest.objects.filter(status = REQUEST_STATUS_NEW)
    logger.info(requests.query)
    logger.info("New Requests number : {}".format(len(requests)))
    print('Command')
    print(id)
    if id:
      requests = requests.filter(id = id)
    for req in requests:
      try:
        process_request(req)
      except Exception as e:
        logger.error(str(e), stack_info=True)
      else:
        logger.info(f'request {req.id} done')
      finally:
        req.status = REQUEST_STATUS_COMPLETED
        req.save()

    logger.info('Completed.')

     # ------------------------------------------------
