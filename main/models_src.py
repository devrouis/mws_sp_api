import re
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .enums import *
from background_task import background
from django.core.management import call_command
import json
from pprint import pprint
from django.conf import settings
# from main.paypal_apis import get_client, update_subscription
from main.mws.utils import ObjectDict


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AppSettings(SingletonModel):
    aws_access_key = models.CharField(max_length=255)
    aws_secret_key = models.CharField(max_length=255)
    request_batch_size = models.IntegerField(default=5)
    default_wait_sec = models.FloatField(default=1.0)
    quota_wait_sec = models.FloatField(default=2.0)
    use_paypal = models.BooleanField(default=False)
    app_id = models.CharField(max_length=255, default='')
    sp_IAM_user_access_key = models.CharField(max_length=255)
    sp_IAM_user_secret_key = models.CharField(max_length=255)
    sp_api_client_id = models.CharField(max_length=255)
    sp_api_client_secret = models.CharField(max_length=255)
    paypal_client_id = models.CharField(
        max_length=255, default='Adt_Vhio0TLBSK1dsw3iOklDv_u-m87eFmdVqAPZ95O7lelQT8hsJ7zodnV2vo6kghB1HuRpBewqabqL')
    paypal_client_secret = models.CharField(
        max_length=255, default='EINVdviKFC5XhnKyuyn6k0nOS1zz_iNxNjqb-Wc_uuR7WxSzZszTNSitz1ScLNNf6sTaXbdu8J-Icod9')
    server_hostname = models.CharField(
        max_length=100, default='www.asin-jan.com')


class UserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    def __str__(self):
        return self.username
    email = models.EmailField(_('Email'), unique=True)
    last_name = models.CharField(
        verbose_name='姓', max_length=255, null=False, blank=False)
    first_name = models.CharField(
        verbose_name='名', max_length=255, null=True, blank=False)
    seller_id = models.CharField(
        max_length=255, blank=False, null=False, unique=True)
    mws_auth_token = models.CharField(max_length=255, blank=False, null=False)
    market_place = models.CharField(max_length=255, blank=False, null=False)
    # -------------------------------------
    sp_api_refresh_token = models.CharField(
        verbose_name='SP-API refresh_token', max_length=500, null=True, blank=False)
    APIs = (
        ('SP-API', 'SP-API'),
        # ('MWS-API', 'MWS-API'),
    )
    api_type = models.CharField(
        max_length=255, choices=APIs, default='SP-API')
   # -------------------------------------
    do_get_matching_product_for_id = models.BooleanField(
        verbose_name='GetMatchingProductForId', default=True)
    do_get_competitive_pricing_for_asin = models.BooleanField(
        verbose_name='GetCompetitivePricingForASIN', default=True)
    do_get_lowest_offer_listings_for_asin = models.BooleanField(
        verbose_name='GetLowestOfferListingsForASIN', default=True)
    do_get_my_price_for_asin = models.BooleanField(
        verbose_name='GetMyPricingForASIN', default=False)
    do_get_product_categories_for_asin = models.BooleanField(
        verbose_name='GetProductCategoriesForASIN', default=False)
    asin_jan_one_to_one = models.BooleanField(
        default=True, verbose_name='JAN検索で一つのASINに絞る')
    paid = models.BooleanField(default=True)

    is_staff = models.BooleanField(
        _('管理者'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('利用開始'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    @property
    def username(self):
        """username属性のゲッター
        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def subscribing(self):
        if self.is_superuser:
            return True
        appsettings = AppSettings.load()
        if appsettings.use_paypal:
            for sub in self.subscriptions.all():
                if sub.status == 'CANCELED':
                    sub.delete()
                    continue
                if sub.status == 'ACTIVE':
                    return True
            return False
        else:
            return self.paid

    @property
    def mysubscription(self):
        s = self.subscriptions.filter(status='ACTIVE')
        if len(s) == 0:
            return None
        return s[0]

# @background(schedule=5)
def async_process_request(request_id):
    call_command('process_requests', id=request_id)

def _extract_id(id_type, id_str):
    if id_type == 'asin':
        pat = '[A-Z0-9]{10}'
    elif id_type == 'jan':
        pat = '[0-9]{13}'

    m = re.match(pat, id_str)
    return m.group() if m != None else None


class ScrapeRequest(models.Model):
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='requests')
    id_type = models.CharField(
        choices=ID_CHOICES, default=ID_ASIN, max_length=10)
    id_text = models.TextField(null=True)
    csv_file = models.FileField(null=True, upload_to='csv')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=1, default=REQUEST_STATUS_NEW, choices=list(REQUEST_STATUS.items()))
    error = models.CharField(max_length=255, null=True, default=None)

    @property
    def id_list(self):
        if self.id_text and self.id_text != '':
            return self.id_text.split('\r\n')
        elif self.csv_file != None:
            with open(self.csv_file.path, mode='r', errors='ignore') as f:
                lines = f.readlines()
                f.close()
            trimmed_list = [_extract_id(self.id_type, line)
                            for line in lines if _extract_id(self.id_type, line)]

            return trimmed_list
        else:
            return []

    @property
    def id_count(self):
        return len(self.id_list)

    @property
    def status_text(self):
        return REQUEST_STATUS.get(self.status)

    @property
    def status_badge_class(self):
        if self.status == REQUEST_STATUS_NEW:
            return 'badge-primary'
        elif self.status == REQUEST_STATUS_IN_PROGRESS:
            return 'badge-warning'
        elif self.status == REQUEST_STATUS_COMPLETED:
            return 'badge-success'
        elif self.status == REQUEST_STATUS_ERROR:
            return 'badge-danger'

    @property
    def downloadable(self):
        return self.status in [REQUEST_STATUS_COMPLETED, REQUEST_STATUS_ERROR]


class ScrapeRequestResult(models.Model):
    scrape_request = models.ForeignKey(
        to=ScrapeRequest, on_delete=models.CASCADE, related_name='results')
    asin = models.CharField(max_length=100, null=True, default=None)
    jan = models.CharField(max_length=13, null=True, default=None)
    get_matching_product_for_id_raw = models.TextField(null=True)
    get_competitive_pricing_for_asin_raw = models.TextField(null=True)
    get_lowest_offer_listings_for_asin_raw = models.TextField(null=True)
    get_my_price_for_asin_raw = models.TextField(null=True)
    get_product_categories_for_asin_raw = models.TextField(null=True)

    @property
    def ItemAttributes(self):
        # if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
        #     return None
        # return json.loads(self.get_matching_product_for_id_raw)['Products']['Product']['AttributeSets']['ItemAttributes']
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        return eval(self.get_matching_product_for_id_raw)['Products']['Product']['AttributeSets']['ItemAttributes']
    @property
    def Binding(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['Binding']['value']
        except KeyError:
            return None
    @property
    def Binding(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['Binding']['value']
        except KeyError:
            return None

    @property
    def PartNumber(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['PartNumber']['value']
        except KeyError:
            return None

    @property
    def Publisher(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['Publisher']['value']
        except KeyError:
            return None

    @property
    def ProductGroup(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['ProductGroup']['value']
        except KeyError:
            return None

    @property
    def ReleaseDate(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['ReleaseDate']['value']
        except KeyError:
            return None

    @property
    def ListPrice(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return (None, None)
        try:
            data = itemattributes['ListPrice']
        except KeyError:
            return (None, None)
        else:
            return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def ListPriceValue(self):
        return self.ListPrice[0]

    @property
    def ListPriceCurrency(self):
        return self.ListPrice[1]

    @property
    def Title(self):
        itemattributes = self.ItemAttributes
        if not itemattributes:
            return None
        try:
            return itemattributes['Title']['value']
        except KeyError:
            return None

    @property
    def SalesRankings(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        try:
            sales_rank_raw = eval(self.get_matching_product_for_id_raw)['Products']['Product']['SalesRankings']['SalesRank']
        except KeyError:
            return None
        else:
            if type(sales_rank_raw) == list:
                # sales_rank_list = [f'{r["ProductCategoryId"]["value"]}:{r["Rank"]["value"]}' for r in sales_rank_raw]
                return sales_rank_raw[0]["Rank"]["value"] if len(sales_rank_raw) > 0 else None
            elif type(sales_rank_raw) in [dict, ObjectDict]:
                # sales_rank_list = [f'{sales_rank_raw["ProductCategoryId"]["value"]}:{sales_rank_raw["Rank"]["value"]}']
                return sales_rank_raw["Rank"]["value"]

    @property
    def PackageDemensions(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        try:
            return eval(self.get_matching_product_for_id_raw)['Products']['Product']['AttributeSets']['ItemAttributes']['PackageDimensions']
        except KeyError:
            return None

    @property
    def Height(self):
        dim = self.PackageDemensions
        if not dim:
            return (None, None)
        try:
            return (dim["Height"]["value"], dim["Height"]["Units"]["value"])
        except KeyError:
            return (None, None)

    @property
    def HeightValue(self):
        return self.Height[0]

    @property
    def HeightUnit(self):
        return self.Height[1]

    @property
    def Length(self):
        dim = self.PackageDemensions
        if not dim:
            return (None, None)
        try:
            return (dim["Length"]["value"], dim["Length"]["Units"]["value"])
        except KeyError:
            return (None, None)

    @property
    def LengthValue(self):
        return self.Length[0]

    @property
    def LengthUnit(self):
        return self.Length[1]

    @property
    def Width(self):
        dim = self.PackageDemensions
        if not dim:
            return (None, None)
        try:
            return (dim["Width"]["value"], dim["Width"]["Units"]["value"])
        except KeyError:
            return (None, None)

    @property
    def WidthValue(self):
        return self.Width[0]

    @property
    def WidthUnit(self):
        return self.Width[1]

    @property
    def Weight(self):
        dim = self.PackageDemensions
        if not dim:
            return (None, None)
        try:
            return (dim["Weight"]["value"], dim["Weight"]["Units"]["value"])
        except KeyError:
            return (None, None)

    @property
    def WeightValue(self):
        return self.Weight[0]

    @property
    def WeightUnit(self):
        return self.Weight[1]

    @property
    def CompetitivePrice(self):
        if not self.get_competitive_pricing_for_asin_raw or self.get_competitive_pricing_for_asin_raw == '':
            return None
        try:
            data = json.loads(self.get_competitive_pricing_for_asin_raw)[
                'Product']['CompetitivePricing']['CompetitivePrices']["CompetitivePrice"]
        except KeyError:
            return None
        else:
            return data

    @property
    def LandedPrice(self):
        data = self.CompetitivePrice
        if not data:
            return (None, None)
        data = data['Price']['LandedPrice']
        return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def LandedPriceValue(self):
        return self.LandedPrice[0]

    @property
    def LandedPriceCurrency(self):
        return self.LandedPrice[1]

    @property
    def Shipping(self):
        data = self.CompetitivePrice
        if not data or 'Shipping' not in data['Price']:
            return (None, None)
        data = data['Price']['Shipping']
        return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def ShippingValue(self):
        return self.Shipping[0]

    @property
    def ShippingCurrency(self):
        return self.Shipping[1]

    @property
    def Points(self):
        data = self.CompetitivePrice
        if not data:
            return (None, None)
        try:
            data = data['Price']['Points']['PointsMonetaryValue']
        except KeyError:
            return (None, None)
        else:
            return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def PointsValue(self):
        return self.Points[0]

    @property
    def PointsCurrency(self):
        return self.Points[1]

    @property
    def OfferListingCount(self):
        if not self.get_competitive_pricing_for_asin_raw or self.get_competitive_pricing_for_asin_raw == '':
            return None
        try:
            data = json.loads(self.get_competitive_pricing_for_asin_raw)[
                'Product']['CompetitivePricing']['NumberOfOfferListings']['OfferListingCount']
        except Exception as e:
            return None
        else:
            return data

    @property
    def OfferListingCountNew(self):
        data = self.OfferListingCount
        if not data:
            return None
        new = [d for d in data if d["condition"]["value"] == 'New']
        return new[0]["value"] if len(new) > 0 else None

    @property
    def OfferListingCountUsed(self):
        data = self.OfferListingCount
        if not data:
            return None

        new = [d for d in data if d["condition"]["value"] == 'Used']
        return new[0]["value"] if len(new) > 0 else None
    from pprint import pprint

    @property
    def LowestOfferListingNew(self):
        if not self.get_lowest_offer_listings_for_asin_raw or self.get_lowest_offer_listings_for_asin_raw == '':
            return None
        try:
            data = json.loads(self.get_lowest_offer_listings_for_asin_raw)[
                'Product']['LowestOfferListings']['LowestOfferListing']
        except Exception as e:
            return None

        if type(data) == list:
            new_listing_price = [
                d["Price"] for d in data if d["Qualifiers"]["ItemCondition"]["value"] == 'New']
        else:
            new_listing_price = [
                data["Price"]] if data["Qualifiers"]["ItemCondition"]["value"] == 'New' else []

        sorted_list = sorted(
            new_listing_price, key=lambda d: d["ListingPrice"]["Amount"]["value"])
        if len(sorted_list) <= 0:
            return None
        else:
            return sorted_list[0]

    @property
    def LowestOfferListingUsed(self):
        if not self.get_lowest_offer_listings_for_asin_raw or self.get_lowest_offer_listings_for_asin_raw == '':
            return None
        try:
            data = json.loads(self.get_lowest_offer_listings_for_asin_raw)[
                'Product']['LowestOfferListings']['LowestOfferListing']
        except Exception as e:
            return None
        if type(data) == list:
            new_listing_price = [
                d["Price"] for d in data if d["Qualifiers"]["ItemCondition"]["value"] == 'Used']
        else:
            new_listing_price = [
                data["Price"]] if data["Qualifiers"]["ItemCondition"]["value"] == 'Used' else []

        sorted_list = sorted(
            new_listing_price, key=lambda d: d["ListingPrice"]["Amount"]["value"])
        if len(sorted_list) <= 0:
            return None
        else:
            return sorted_list[0]

    @property
    def LowestOfferListingNewPrice(self):
        data = self.LowestOfferListingNew
        if not data:
            return (None, None)
        return (data["ListingPrice"]["Amount"]["value"], data["ListingPrice"]["CurrencyCode"]["value"])

    @property
    def LowestOfferListingNewPriceValue(self):
        return self.LowestOfferListingNewPrice[0]

    @property
    def LowestOfferListingNewPriceCurrency(self):
        return self.LowestOfferListingNewPrice[1]

    @property
    def LowestOfferListingNewShipping(self):
        data = self.LowestOfferListingNew
        if not data or 'Shipping' not in data:
            return (None, None)
        return (data["Shipping"]["Amount"]["value"], data["Shipping"]["CurrencyCode"]["value"])

    @property
    def LowestOfferListingNewShippingValue(self):
        return self.LowestOfferListingNewShipping[0]

    @property
    def LowestOfferListingNewShippingCurrency(self):
        return self.LowestOfferListingNewShipping[1]

    @property
    def LowestOfferListingNewPoints(self):
        data = self.LowestOfferListingNew
        if not data:
            return (None, None)
        data = data["Points"]["PointsMonetaryValue"]
        return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def LowestOfferListingNewPointsValue(self):
        return self.LowestOfferListingNewPoints[0]

    @property
    def LowestOfferListingNewPointsCurrency(self):
        return self.LowestOfferListingNewPoints[1]

    @property
    def LowestOfferListingUsedPrice(self):
        data = self.LowestOfferListingUsed
        if not data:
            return (None, None)
        return (data["ListingPrice"]["Amount"]["value"], data["ListingPrice"]["CurrencyCode"]["value"])

    @property
    def LowestOfferListingUsedPriceValue(self):
        return self.LowestOfferListingUsedPrice[0]

    @property
    def LowestOfferListingUsedPriceCurrency(self):
        return self.LowestOfferListingUsedPrice[1]

    @property
    def LowestOfferListingUsedShipping(self):
        data = self.LowestOfferListingUsed
        if not data:
            return (None, None)
        return (data["Shipping"]["Amount"]["value"], data["Shipping"]["CurrencyCode"]["value"])

    @property
    def LowestOfferListingUsedShippingValue(self):
        return self.LowestOfferListingUsedShipping[0]

    @property
    def LowestOfferListingUsedShippingCurrency(self):
        return self.LowestOfferListingUsedShipping[1]

    @property
    def LowestOfferListingUsedPoints(self):
        data = self.LowestOfferListingUsed
        if not data:
            return (None, None)
        data = data["Points"]["PointsMonetaryValue"]
        return (data["Amount"]["value"], data["CurrencyCode"]["value"])

    @property
    def LowestOfferListingUsedPointsValue(self):
        return self.LowestOfferListingUsedPoints[0]

    @property
    def LowestOfferListingUsedPointsCurrency(self):
        return self.LowestOfferListingUsedPoints[1]

    CSV_HEADERS = [
        "ASIN",
        "JAN",
        "タイトル",
        "出版社・メーカー",
        "型番",
        "ランキング",
        "Binding",
        "カテゴリ",
        "リリース",
        "定価",
        "定価通貨",
        "BuyBox価格",
        "BuyBox価格通貨",
        "送料",
        "送料通貨",
        "ポイント(B)",
        "ポイント(B) 通貨",
        "新品数",
        "新品最安値",
        "新品最安値通貨",
        "新品最安値送料",
        "新品最安値送料通貨",
        "新品最安値ポイント",
        "新品最安値ポイント通貨",
        "中古数",
        "中古最安値",
        "中古最安値通貨",
        "中古最安値送料",
        "中古最安値送料通貨",
        "中古最安値ポイント",
        "中古最安値ポイント通貨",
        "発送重量",
        "発送重量単位",
        "高さ(梱包)",
        "高さ(梱包)単位",
        "長さ(梱包)",
        "長さ(梱包)単位",
        "幅(梱包)",
        "幅(梱包)単位",
    ]
    CSV_HEADERS_JAN = [
        "JAN",
        "ASIN",
        "タイトル",
        "出版社・メーカー",
        "型番",
        "ランキング",
        "Binding",
        "カテゴリ",
        "リリース",
        "定価",
        "定価通貨",
        "BuyBox価格",
        "BuyBox価格通貨",
        "送料",
        "送料通貨",
        "ポイント(B)",
        "ポイント(B) 通貨",
        "新品数",
        "新品最安値",
        "新品最安値通貨",
        "新品最安値送料",
        "新品最安値送料通貨",
        "新品最安値ポイント",
        "新品最安値ポイント通貨",
        "中古数",
        "中古最安値",
        "中古最安値通貨",
        "中古最安値送料",
        "中古最安値送料通貨",
        "中古最安値ポイント",
        "中古最安値ポイント通貨",
        "発送重量",
        "発送重量単位",
        "高さ(梱包)",
        "高さ(梱包)単位",
        "長さ(梱包)",
        "長さ(梱包)単位",
        "幅(梱包)",
        "幅(梱包)単位",
    ]

    @property
    def csv_columns(self):
        return [
            ("ASIN", self.asin),
            ("JAN", self.jan),
            ("タイトル", self.Title),
            ("出版社・メーカー", self.Publisher),
            ("型番", self.PartNumber),
            ("ランキング", self.SalesRankings),
            ("Binding", self.Binding),
            ("カテゴリ", self.ProductGroup),
            ("リリース", self.ReleaseDate),
            ("定価", self.ListPrice[0]),
            ("定価通貨", self.ListPrice[1]),
            ("BuyBox価格", self.LandedPrice[0]),
            ("BuyBox価格通貨", self.LandedPrice[1]),
            ("送料", self.Shipping[0]),
            ("送料通貨", self.Shipping[1]),
            ("ポイント(B)", self.Points[0]),
            ("ポイント(B) 通貨", self.Points[1]),
            ("新品数", self.OfferListingCountNew),
            ("新品最安値", self.LowestOfferListingNewPrice[0]),
            ("新品最安値通貨", self.LowestOfferListingNewPrice[1]),
            ("新品最安値送料", self.LowestOfferListingNewShipping[0]),
            ("新品最安値送料通貨", self.LowestOfferListingNewShipping[1]),
            ("新品最安値ポイント", self.LowestOfferListingNewPoints[0]),
            ("新品最安値ポイント通貨", self.LowestOfferListingNewPoints[1]),
            ("中古数", self.OfferListingCountUsed),
            ("中古最安値", self.LowestOfferListingUsedPrice[0]),
            ("中古最安値通貨", self.LowestOfferListingUsedPrice[1]),
            ("中古最安値送料", self.LowestOfferListingUsedShipping[0]),
            ("中古最安値送料通貨", self.LowestOfferListingUsedShipping[1]),
            ("中古最安値ポイント", self.LowestOfferListingUsedPoints[0]),
            ("中古最安値ポイント通貨", self.LowestOfferListingUsedPoints[1]),
            ("発送重量", self.Weight[0]),
            ("発送重量単位", self.Weight[1]),
            ("高さ(梱包)", self.Height[0]),
            ("高さ(梱包)単位", self.Height[1]),
            ("長さ(梱包)", self.Length[0]),
            ("長さ(梱包)単位", self.Length[1]),
            ("幅(梱包)", self.Width[0]),
            ("幅(梱包)単位", self.Width[1]),
        ]

    @property
    def csv_column_headers(self):
        return [v[0] for v in self.csv_columns]

    @property
    def csv_column_values(self):
        return [v[1] for v in self.csv_columns]


class PaypalSubscription(models.Model):
    plan_id = models.CharField(max_length=100)
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=100)
    subscription_id = models.CharField(max_length=255, primary_key=True)
    approve_url = models.CharField(max_length=100)
    ba_token = models.CharField(max_length=100, null=True, default=None)
    token = models.CharField(max_length=100, null=True, default=None)
