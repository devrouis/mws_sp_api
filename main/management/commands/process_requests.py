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
from sp_api.api import Orders
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

def parse_and_save_result(req, operation_name, result_dict, asin, jan, asin_list, jan_list):
  # if req.id_type == ID_ASIN:
    # asin = result_dict['asin']
  # if 'Id' in result_dict: # for get_matching_product_for_id response
  #   asin = result_dict['Id']['value']
  # if 'ASIN' in result_dict:
  #   asin = result_dict['Products']['Product']['ASIN']['value']
  # asin_index = asin_list.index(asinValue)
  save_to_db(req, operation_name, result_dict, asin, jan)

def merge_dict(d1, d2):
  dd = defaultdict(list)

  for d in (d1, d2):
      for key, value in d.items():
          if isinstance(value, list):
              dd[key].extend(value)
          else:
              dd[key].append(value)
  return dict(dd)

def process_request(req):
  # credentials=dict(
  #     refresh_token=req.user.sp_api_refresh_token,
  #     lwa_app_id=appsettings.sp_api_client_id,
  #     lwa_client_secret=appsettings.sp_api_client_secret,
  #     aws_secret_key=appsettings.sp_IAM_user_secret_key,
  #     aws_access_key=appsettings.sp_IAM_user_access_key,
  #     # role_arn = 'arn:aws:iam::072834111115:role/ASIN_JAN_ROLE'
  # )
  # response = Orders(credentials=credentials).get_orders(CreatedAfter='TEST_CASE_200', MarketplaceIds=["ATVPDKIKX0DER"])
  # print('***response start***')
  # print(response)
  # print('***response end***')
  req.status = REQUEST_STATUS_IN_PROGRESS
  req.save()



  operations = [f.name.replace('do_', '') for f in User._meta.fields if 'do_' in f.name and getattr(req.user, f.name)]
  
  api = get_api(req.user)
  logger.info("now processing {}".format(req.id))

  # if query by jan
  asin_jan_pairs = []

  sp_get_token_param = {
    "SPAPI_LWA_Client_ID" : appsettings.sp_api_client_id,
    "SPAPI_LWA_Client_PW" : appsettings.sp_api_client_secret,
    "SPAPI_REFRESH_TOKEN" : req.user.sp_api_refresh_token
  }

  asinItem = None
  janItem = None
  
  if req.id_type == ID_ASIN :
    if req.user.api_type == SP:
      token=SPAPI_Get_Token(sp_get_token_param)
      SPAPI_Access_Token=token[0] 
      # CatalogItems = SPAPI_GetCatalogItems("", req.id_list, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token)
      ProductsItemOffers = SPAPI_GetProductsItemOffers("", req.id_list, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token)
      # for asin in req.id_list:
      #   data = []
      #   # sp_api_start()
      #   token=SPAPI_Get_Token(sp_get_token_param)
      #   SPAPI_Access_Token=token[0] 
      #   CatalogItem = SPAPI_GetCatalogItemsForASIN(asin, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token)
      #   NewProductPrice = SPAPI_GetProductsPriceForAsin(asin, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token, 'new')
      #   UsedProductPrice = SPAPI_GetProductsPriceForAsin(asin, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token, 'used')
      #   combined_dct1 = merge_dict(CatalogItem, NewProductPrice)
      #   combined_dct2 = merge_dict(combined_dct1, UsedProductPrice)
        
      #   data =  json.dumps(combined_dct2)
      #   combined_json = SP_API_NEW_FORMATTING(json.loads(data))

      #   asinItem = asin

      #   parse_and_save_result(req, 'operation_name', json.dumps(combined_json), asinItem, janItem, 'asin_list', 'jan_list')

        # if type(data) in [dict, ObjectDict]: # if single product
        #   parse_and_save_result(req, 'operation_name', res, asinItem, janItem, 'asin_list', 'jan_list')
        # elif type(data) == list: # if multiple products
        #   for item in data:
        #     parse_and_save_result(req, 'operation_name', item, asinItem, janItem, 'asin_list', 'jan_list')
        # products = res['Products']['Product']

        # if type(products) == list:
        #   if req.user.asin_jan_one_to_one:
        #     print('one to one')
        #     no_set = [p for p in products if 'Binding' in p['AttributeSets']['ItemAttributes'] and p['AttributeSets']['ItemAttributes']['Binding']['value'] != 'セット買い']
        #     if len(no_set) > 0:
        #       asin_jan_pairs.append((asin, None))
        #     else:
        #       ranked = [p for p in products if 'SalesRankings' in p and 'SalesRank' in p['SalesRankings']]
        #       s = sorted(ranked, key=lambda p: p['SalesRankings']['SalesRank'][0]['Rank']['value'] if type(p['SalesRankings']['SalesRank']) == list else p['SalesRankings']['SalesRank']['Rank']['value'])
        #       if len(s) > 0:
        #         asin_jan_pairs.append((s[0]['Identifiers']['MarketplaceASIN']['ASIN']['value'], None))
        #   else:
        #     asin_jan_pairs.extend([(p['Identifiers']['MarketplaceASIN']['ASIN']['value'], None) for p in products])
        # elif type(products) in [dict, ObjectDict]:
        #   asin_jan_pairs.extend([(products['Identifiers']['MarketplaceASIN']['ASIN']['value'], None)])
        # else:
        #   logger.error(f'unexpected type {type(products)}')
        #   return
  #------ get sp-api catalogItems for ASIN end-------

    # else:
    #   asin_jan_pairs = [(asin, None) for asin in req.id_list]

  elif req.id_type == ID_JAN:
    for jan in req.id_list:
      try:
  #------ get sp-api catalogItems for JAN start-------        
        if req.user.api_type == SP:
          token=SPAPI_Get_Token(sp_get_token_param)
          SPAPI_Access_Token=token[0]
          CatalogItem = SPAPI_GetCatalogItemsForJAN(jan, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token)
          asin = CatalogItem['payload']['Items'][0]['Identifiers']['MarketplaceASIN']['ASIN']
          CatalogItem['payload'] = CatalogItem['payload']['Items'][0]
          NewProductPrice = SPAPI_GetProductsPriceForAsin(asin, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token, 'new')
          UsedProductPrice = SPAPI_GetProductsPriceForAsin(asin, appsettings.sp_IAM_user_access_key, appsettings.sp_IAM_user_secret_key, req.user.market_place, SPAPI_Access_Token, 'used')
          combined_dct1 = merge_dict(CatalogItem, NewProductPrice)
          combined_dct2 = merge_dict(combined_dct1, UsedProductPrice)
        
          data =  json.dumps(combined_dct2)
          combined_json = SP_API_NEW_FORMATTING(json.loads(data))
          
          print('**** NewProductPrice ****')
          print(NewProductPrice)
          print('**** UsedProductPrice ****')
          print(UsedProductPrice)
          print('**** Combined Json ****')
          print(combined_json)


          asinItem = asin
          janItem = jan
          


          parse_and_save_result(req, 'operation_name', json.dumps(combined_json), asinItem, janItem, 'asin_list', 'jan_list')
        # else:
        #   res = get_matching_product_for_id(api, req.user.market_place, [jan], id_type = 'JAN')        
  #------ get sp-api catalogItems for JAN start------- 
          
        # if 'Error' in res:
        #   raise Exception(res["Error"]["Message"]["value"])
      except Exception as e:
        logger.error(e, stack_info=True)
        save_to_db(req, None, { 'Error': str(e) }, None, jan = jan)
        continue        
  
      # products = res['Products']['Product']

      # if type(products) == list:
      #   if req.user.asin_jan_one_to_one:
      #     print('one to one')
      #     no_set = [p for p in products if 'Binding' in p['AttributeSets']['ItemAttributes'] and p['AttributeSets']['ItemAttributes']['Binding']['value'] != 'セット買い']
      #     if len(no_set) > 0:
      #       asin_jan_pairs.append((no_set[0]['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan))
      #     else:
      #       ranked = [p for p in products if 'SalesRankings' in p and 'SalesRank' in p['SalesRankings']]
      #       s = sorted(ranked, key=lambda p: p['SalesRankings']['SalesRank'][0]['Rank']['value'] if type(p['SalesRankings']['SalesRank']) == list else p['SalesRankings']['SalesRank']['Rank']['value'])
      #       if len(s) > 0:
      #         asin_jan_pairs.append((s[0]['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan))
      #   else:
      #     asin_jan_pairs.extend([(p['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan) for p in products])
      # elif type(products) in [dict, ObjectDict]:
      #   asin_jan_pairs.extend([(products['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan)])
      # else:
      #   logger.error(f'unexpected type {type(products)}')
      #   return
    
  # for id_chunk in chunks(asin_jan_pairs, appsettings.request_batch_size):
  #   asin_list = [e[0] for e in id_chunk]
  #   jan_list = [e[1] for e in id_chunk]

  #   for operation_name in operations:
  #     logger.info(f'{operation_name}...')
  #     sleep(appsettings.default_wait_sec)
  #     operation = globals()[operation_name]
  #     try:
  #       result = operation(api, req.user.market_place, asin_list)
  #       if 'Error' in result:
  #         raise Exception(result['Error'])
  #     except Exception as e:
  #       sleep(appsettings.quota_wait_sec)
  #       # retry 
  #       try:
  #         result = operation(api, req.user.market_place, asin_list)
  #       except Exception as e:
  #         logger.error(str(e), stack_info=True)
  #         break
  # if type(data) in [dict, ObjectDict]: # if single product
  #   parse_and_save_result(req, 'operation_name', data, asinItem, jan, 'asin_list', 'jan_list')
  # elif type(data) == list: # if multiple products
  #   for item in data:
  #     parse_and_save_result(req, 'operation_name', item, asinItem, jan, 'asin_list', 'jan_list')
        
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

