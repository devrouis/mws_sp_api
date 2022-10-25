
import time
import base64
from paypalhttp import Environment, HttpClient
import ssl
import platform
import requests
from main.models import PaypalSubscription
import json
from main.enums import *
from urllib.parse import urlencode

class AccessToken(object):
  def __init__(self, access_token, expires_in, token_type):
    self.access_token = access_token
    self.expires_in = expires_in
    self.token_type = token_type
    self.created_at = time.time()

  def is_expired(self):
    return self.created_at + self.expires_in <= time.time()

  def authorization_string(self):
    return "{0} {1}".format(self.token_type, self.access_token)

class AccessTokenRequest:
  def __init__(self, paypal_environment, refresh_token=None):
    self.path = "/v1/oauth2/token"
    self.verb = "POST"
    self.body = {}
    if refresh_token:
      self.body['grant_type'] = 'refresh_token'
      self.body['refresh_token'] = refresh_token
    else:
      self.body['grant_type'] = 'client_credentials'

    self.headers = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": paypal_environment.authorization_string()
    }

class RefreshTokenRequest:
  def __init__(self, paypal_environment, authorization_code):
    self.path = "/v1/identity/openidconnect/tokenservice"
    self.verb = "POST"
    self.body = {
            'grant_type': 'authorization_code',
            'code': authorization_code
            }
    self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": paypal_environment.authorization_string()
            }

class PayPalEnvironment(Environment):
  LIVE_API_URL = 'https://api.paypal.com'
  LIVE_WEB_URL = 'https://www.paypal.com'
  SANDBOX_API_URL = 'https://api.sandbox.paypal.com'
  SANDBOX_WEB_URL = 'https://www.sandbox.paypal.com'

  def __init__(self, client_id, client_secret, apiUrl, webUrl):
    super(PayPalEnvironment, self).__init__(apiUrl)
    self.client_id = client_id
    self.client_secret = client_secret
    self.web_url = webUrl

  def authorization_string(self):
    return "Basic {0}".format(base64.b64encode((self.client_id + ":" + self.client_secret).encode()).decode())


class SandboxEnvironment(PayPalEnvironment):

  def __init__(self, client_id, client_secret):
    super(SandboxEnvironment, self).__init__(client_id,
          client_secret,
          PayPalEnvironment.SANDBOX_API_URL,
          PayPalEnvironment.SANDBOX_WEB_URL)

class LiveEnvironment(PayPalEnvironment):

  def __init__(self, client_id, client_secret):
    super(LiveEnvironment, self).__init__(client_id,
          client_secret,
          PayPalEnvironment.LIVE_API_URL,
          PayPalEnvironment.LIVE_WEB_URL)

USER_AGENT = 'python client'

class PayPalHttpClient(HttpClient):
  def __init__(self, environment, refresh_token=None):
    HttpClient.__init__(self, environment)
    self._refresh_token = refresh_token
    self._access_token = None
    self.environment = environment

    self.add_injector(injector=self)

  def get_user_agent(self):
    return USER_AGENT

  def __call__(self, request):
    request.headers["sdk_name"] = "Checkout SDK"
    request.headers["sdk_version"] = "1.0.1"
    request.headers["sdk_tech_stack"] = "Python" + platform.python_version()
    request.headers["api_integration_type"] = "PAYPALSDK"

    if "Accept-Encoding" not in request.headers:
      request.headers["Accept-Encoding"] = "gzip"

    if "Authorization" not in request.headers and not isinstance(request, AccessTokenRequest) and not isinstance(request, RefreshTokenRequest):
      if not self._access_token or self._access_token.is_expired():
        accesstokenresult = self.execute(AccessTokenRequest(self.environment, self._refresh_token)).result
        self._access_token = AccessToken(access_token=accesstokenresult.access_token,
                                        expires_in=accesstokenresult.expires_in,
                                        token_type=accesstokenresult.token_type)

      request.headers["Authorization"] = self._access_token.authorization_string()


    from urllib.parse import quote  # Python 3+

class BaseRequest:
  def __init__(self):
    self.path = ''
    self.headers = {}
    self.headers["Content-Type"] = "application/json"
    self.body = None

  def prefer(self, prefer):
    self.headers["Prefer"] = str(prefer)
  
  def request_id(self, request_id):
    self.headers["PayPal-Request-Id"] = request_id

  def request_body(self, params):
    self.body = params
    return self
  
  def query_param(self, params):
    self.path = f'{self.path}?{urlencode(params)}'

class CreateProductRequest(BaseRequest):
  def __init__(self):
    super().__init__()
    self.verb = "POST"
    self.path = "/v1/catalogs/products/"

class ListProductRequest(BaseRequest):
  def __init__(self):
    super().__init__()
    self.verb = "GET"
    self.path = "/v1/catalogs/products/"
  
class CreateBillingPlanRequest(BaseRequest):
  def __init__(self):
    super().__init__()
    self.verb = "POST"
    self.path = "/v1/billing/plans/"

class ListBillingPlanRequest(BaseRequest):
  def __init__(self):
    super().__init__()
    self.verb = "GET"
    self.path = "/v1/billing/plans/"

class CreateSubscriptionRequest(BaseRequest):
  def __init__(self):
    super().__init__()
    self.verb = "POST"
    self.path = "/v1/billing/subscriptions/"

class CancelSubscriptionRequest(BaseRequest):
  def __init__(self, id):
    super().__init__()
    self.verb = "POST"
    self.path = f"/v1/billing/subscriptions/{id}/cancel"

class GetSubscriptionRequest(BaseRequest):
  def __init__(self, id):
    super().__init__()
    self.verb = "GET"
    self.path = f"/v1/billing/subscriptions/{id}"
 

def get_client(client_id, client_secret):
  environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
  return PayPalHttpClient(environment)

def list_products(client):
  request = ListProductRequest()
  try:
    response = client.execute(request)
  except IOError as ioe:
    print(ioe)
    return None
  else:
    return response.result.products

def create_default_product(client):
  product_name = 'default product'
  params = {
    "id": PP_DEFAULT_PRODUCT_ID,
    "name": product_name,
    "type": "SERVICE",
    "category": "SOFTWARE",
    # "image_url": "https://example.com/streaming.jpg",
    # "home_url": "https://example.com/home"
  }
  request = CreateProductRequest()
  request.prefer('return=minimal')
  request.request_body(params)

  try:
    # Call API with your client and get a response for your call
    response = client.execute(request)
  except IOError as ioe:
    print(ioe)
    return None
  else:
    product_id = response.result.id
    return product_id

def list_billing_plans(client):
  request = ListBillingPlanRequest()
  request.query_param({ 'product_id': PP_DEFAULT_PRODUCT_ID })
  try:
    response = client.execute(request)
  except IOError as ioe:
    print(ioe)
    return None
  else:
    print(response.result)
    return response.result.plans

def create_default_plan(client):
  params = {
    "product_id": PP_DEFAULT_PRODUCT_ID,
    "name": "問屋ハンター 利用権",
    "description": "問屋ハンターのシステム利用権を購入できます。",
    "status": "ACTIVE",
    "billing_cycles": [
      {
        "frequency": {
          "interval_unit": "MONTH",
          "interval_count": 1
        },
        "tenure_type": "TRIAL",
        "sequence": 1,
        "total_cycles": 1,
        "pricing_scheme": {
          "fixed_price": {
            "value": "0",
            "currency_code": "JPY"
          }
        }
      },
      {
        "frequency": {
          "interval_unit": "MONTH",
          "interval_count": 1
        },
        "tenure_type": "REGULAR",
        "sequence": 2,
        "total_cycles": 0,
        "pricing_scheme": {
          "fixed_price": {
            "value": "100",
            "currency_code": "JPY"
          }
        }
      }
    ],
    "payment_preferences": {
      "auto_bill_outstanding": True,
      "setup_fee": {
        "value": "0",
        "currency_code": "JPY"
      },
      "setup_fee_failure_action": "CONTINUE",
      "payment_failure_threshold": 3
    },
    "taxes": {
      "percentage": "0",
      "inclusive": False
    }
  }
  request = CreateBillingPlanRequest()
  request.prefer('return=minimal')
  request.request_body(params)

  try:
    # Call API with your client and get a response for your call
    response = client.execute(request)
  except IOError as ioe:
    print(ioe)
    return None
  else:
    status = response.result.status
    print(f'plan is {status}')
    plan_id = response.result.id
    return plan_id

def create_subscription(client, user, plan_id, return_url = None, cancel_url = None):
  params = {
    "plan_id": plan_id,
    "quantity": "1",
    "shipping_amount": {
      "currency_code": "JPY",
      "value": "0"
    },
    "subscriber": {
      "name": {
        "given_name": user.last_name,
        "surname": user.first_name
      },
      "email_address": user.email
    },
    "application_context": {
      "brand_name": "問屋ハンター",
      "locale": "ja-JP",
      "shipping_preference": "NO_SHIPPING",
      "user_action": "SUBSCRIBE_NOW",
      "payment_method": {
        "payer_selected": "PAYPAL",
        "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
      },
      "return_url": return_url,
      "cancel_url": cancel_url
    }
  }
  request = CreateSubscriptionRequest()
  # request.prefer('return=minimal')
  request.request_body(params)

  try:
    # Call API with your client and get a response for your call
    response = client.execute(request)
  except Exception as e:
    print(request)
    print(f'error {e}')
    return None
  else:
    subscription_id = response.result.id
    status = response.result.status
    approve_url = None
    for link in response.result.links:
      if link.rel == 'approve':
        approve_url = link.href
    if not approve_url:
      print('approve link not found')
      return None

    subscription = PaypalSubscription(user = user, plan_id = plan_id, status = status, subscription_id = subscription_id, approve_url = approve_url)
    subscription.save()
    return subscription

def cancel_subscription(client, subscription):
  request = CancelSubscriptionRequest(subscription.subscription_id)
  try:
    response = client.execute(request)
  except Exception as e:
    print(e)
    return None
  else:
    subscription.status = 'CANCELED'
    subscription.save()
    return subscription

def update_subscription(client, subscription):
  request = GetSubscriptionRequest(subscription.subscription_id)
  try:
    response = client.execute(request)
  except Exception as e:
    print(e)
    return None
  else:
    subscription.status = response.result.status
    subscription.save()
    return subscription