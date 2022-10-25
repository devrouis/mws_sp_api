from .models import User, ScrapeRequest, AppSettings
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
import io, re, csv
class SignupForm(UserCreationForm):
  class Meta:
    model = User
    fields = ('email', 'last_name', 'first_name', 'seller_id', 'mws_auth_token','sp_api_refresh_token', 'market_place', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
  """ユーザー情報更新フォーム"""
  class Meta:
    model = User
    fields = ('email', 'last_name', 'first_name', 'seller_id', 'mws_auth_token', 'sp_api_refresh_token', 'market_place', 'api_type', 'do_get_matching_product_for_id', 'do_get_competitive_pricing_for_asin', 'do_get_lowest_offer_listings_for_asin', 'do_get_my_price_for_asin', 'do_get_product_categories_for_asin', 'asin_jan_one_to_one')

class SettingUpdateForm(forms.ModelForm):
  """ユーザー情報更新フォーム"""
  class Meta:
    model = AppSettings
    fields = ('aws_access_key', "aws_secret_key", "sp_IAM_user_access_key", "sp_IAM_user_secret_key", "sp_api_client_id", "sp_api_client_secret","app_id")

class RequestTextForm(forms.ModelForm):
  class Meta:
    model = ScrapeRequest
    fields = ('id_type', 'id_text',)
  # text = forms.CharField(widget=forms.Textarea)
  
  def clean(self):
    data= super().clean()
    id_type = data['id_type']
    id_text = data['id_text']
    pattern = r'^[A-Z0-9]{10}$' if id_type == 'asin' else r'^[0-9]{13}$' 
    for index, id in enumerate(id_text.split('\r\n')):
      if not re.fullmatch(pattern, id):
        raise forms.ValidationError(f'{index + 1}個目のIDが不正です。...')
    return data
class RequestCsvForm(forms.ModelForm):
  class Meta:
    model = ScrapeRequest
    fields = ('id_type', 'csv_file',)
  
  def clean(self):
    data = super().clean()
    id_type = data['id_type']
    csv_file = data['csv_file']
    decoded_file = csv_file.read().decode('utf-8-sig')
    io_string = io.StringIO(decoded_file)

    pattern = r'^[A-Z0-9]{10}$' if id_type == 'asin' else r'^[0-9]{13}$' 
    for index, row in enumerate(csv.reader(io_string)):
      id = row[0].replace('\r', '')
      id = id.strip()
      if not re.fullmatch(pattern, id):
        raise forms.ValidationError(f'{index + 1}個目のIDが不正です。..')
    return data
