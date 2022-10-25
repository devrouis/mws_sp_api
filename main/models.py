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
    def AttributeSets(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        return json.loads(self.get_matching_product_for_id_raw)["payload"][0]["AttributeSets"][0]

    @property
    def Title(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["Title"]
        except KeyError:
            return None
    
    @property
    def Publisher(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["Publisher"]
        except KeyError:
            return None

    @property
    def PartNumber(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["PartNumber"]
        except KeyError:
            return None

    @property
    def ProductGroup(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["ProductGroup"]
        except KeyError:
            return None

    @property
    def PackageDimensionsWeight(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["PackageDimensions"]["Weight"]["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsHeight(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["PackageDimensions"]["Height"]["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsLength(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["PackageDimensions"]["Length"]["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsWidth(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["PackageDimensions"]["Width"]["value"]
        except KeyError:
            return None

    @property
    def SmallImage(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["SmallImage"]["URL"]
        except KeyError:
            return None

    @property
    def NewProductSummary(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        return json.loads(self.get_matching_product_for_id_raw)["payload"][1]["Summary"]

    @property
    def SalesRankingOneId(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["SalesRankings"][0]["ProductCategoryId"]
        except KeyError:
            return None
    
    @property
    def SalesRankingOneRank(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["SalesRankings"][0]["Rank"]
        except KeyError:
            return None

    @property
    def SalesRankingTwoId(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["SalesRankings"][1]["ProductCategoryId"]
        except KeyError:
            return None
    
    @property
    def SalesRankingTwoRank(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["SalesRankings"][1]["Rank"]
        except KeyError:
            return None
    
    @property
    def ListPriceAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["ListPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def ListPriceAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["ListPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPriceLandAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["BuyBoxPrices"][0]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPriceShippingAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["BuyBoxPrices"][0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPricePointsNumber(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["BuyBoxPrices"][0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def AmazonNewLowestLandPriceAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][0]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonNewLowestShippingAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonNewLowestPointsNumber(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def AmazonOfferCount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["NumberOfOffers"][0]["OfferCount"] 

        except KeyError:
            return None
    
    @property
    def MerchantNewLowestLandPriceAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][1]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantNewLowestShippingAmount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][1]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantNewLowestPointsNumber(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["LowestPrices"][1]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def MerchantOfferCount(self):
        newproductsummary = self.NewProductSummary
        if not newproductsummary:
            return None
        try:
            return newproductsummary["NumberOfOffers"][1]["OfferCount"] 
        except KeyError:
            return None
    
    @property
    def UsedProductSummary(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        return json.loads(self.get_matching_product_for_id_raw)["payload"][2]["Summary"]

    @property
    def AmazonUsedLowestLandPriceAmount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][0]["LandedPrice"]["Amount"]
        except:
            return None
    
    @property
    def AmazonUsedLowestShippingAmount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonUsedLowestPointsNumber(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def AmazonUsedOfferCount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["NumberOfOffers"][0]["OfferCount"] 
        except KeyError:
            return None

    @property
    def MerchantUsedLowestLandPriceAmount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][1]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedLowestShippingAmount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][1]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedLowestPointsNumber(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["LowestPrices"][1]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedOfferCount(self):
        usedproductsummary = self.UsedProductSummary
        if not usedproductsummary:
            return None
        try:
            return usedproductsummary["NumberOfOffers"][1]["OfferCount"] 
        except KeyError:
            return None

    CSV_HEADERS = [
        "ASIN",
        "JAN",
        "タイトル",
        "出版社・メーカー",
        "型番",
        "ランキング名1",
        "ランキング1",
        "ランキング名2",
        "ランキング2",
        "カテゴリ",
        # "ProductTypeName",	
        "定価",
        "BuyBox価格",
        "BuyBox送料",
        "BuyBoxポイント",
        "Amazon新品最安値",
        "Amazon新品送料",
        "Amazon新品ポイント",
        "Amazon新品数",
        "Merchant新品最安値",
        "Merchant新品送料",
        "Merchant新品ポイント",
        "Merchant新品数",
        "Amazon中古最安値",
        "Amazon中古送料",
        "Amazon中古ポイント",
        "Amazon中古数",
        "Merchant中古最安値",
        "Merchant中古送料",
        "Merchant中古ポイント",
        "Merchant中古数",
        "発送重量",	
        "高さ(梱包)",         
        "長さ(梱包)",       
        "幅(梱包)",
        "画像" 
    ]
    CSV_HEADERS_JAN = [
        "JAN",
        "ASIN",
        "タイトル",
        "出版社・メーカー",
        "型番",
        "ランキング名1",
        "ランキング1",
        "ランキング名2",
        "ランキング2",
        "カテゴリ",
        # "ProductTypeName",	
        "定価",
        "BuyBox価格",
        "BuyBox送料",
        "BuyBoxポイント",
        "Amazon新品最安値",
        "Amazon新品送料",
        "Amazon新品ポイント",
        "Amazon新品数",
        "Merchant新品最安値",
        "Merchant新品送料",
        "Merchant新品ポイント",
        "Merchant新品数",
        "Amazon中古最安値",
        "Amazon中古送料",
        "Amazon中古ポイント",
        "Amazon中古数",
        "Merchant中古最安値",
        "Merchant中古送料",
        "Merchant中古ポイント",
        "Merchant中古数",
        "発送重量",	
        "高さ(梱包)",         
        "長さ(梱包)",       
        "幅(梱包)",
        "画像" 
    ]

    @property
    def csv_columns(self):
        return [
                ("JAN", self.asin),
                ("ASIN", self.jan),
                ("タイトル", self.Title),
                ("出版社・メーカー", self.Publisher),
                ("型番", self.PartNumber),
                ("ランキング名1", self.SalesRankingOneId),
                ("ランキング1", self.SalesRankingOneRank),
                ("ランキング名2", self.SalesRankingTwoId),
                ("ランキング2", self.SalesRankingTwoRank),
                ("カテゴリ", self.ProductGroup),
                # ("ProductTypeName",	),
                ("定価", self.ListPriceAmount),
                ("BuyBox価格", self.BuyBoxPriceLandAmount),
                ("BuyBox送料", self.BuyBoxPriceShippingAmount),
                ("BuyBoxポイント", self.BuyBoxPricePointsNumber),
                ("Amazon新品最安値", self.AmazonNewLowestLandPriceAmount),
                ("Amazon新品送料", self.AmazonNewLowestShippingAmount),
                ("Amazon新品ポイント", self.AmazonNewLowestPointsNumber),
                ("Amazon新品数", self.AmazonOfferCount),
                ("Merchant新品最安値", self.MerchantNewLowestLandPriceAmount),
                ("Merchant新品送料", self.MerchantNewLowestShippingAmount),
                ("Merchant新品ポイント", self.MerchantNewLowestPointsNumber),
                ("Merchant新品数", self.MerchantOfferCount),
                ("Amazon中古最安値", self.AmazonUsedLowestLandPriceAmount),
                ("Amazon中古送料", self.AmazonUsedLowestShippingAmount),
                ("Amazon中古ポイント", self.AmazonUsedLowestPointsNumber),
                ("Amazon中古数", self.AmazonUsedOfferCount),
                ("Merchant中古最安値", self.MerchantUsedLowestLandPriceAmount),
                ("Merchant中古送料", self.MerchantUsedLowestShippingAmount),
                ("Merchant中古ポイント", self.MerchantUsedLowestPointsNumber),
                ("Merchant中古数", self.MerchantUsedOfferCount),
                ("発送重量", self.PackageDimensionsWeight),
                ("高さ(梱包)", self.PackageDimensionsHeight),
                ("長さ(梱包)", self.PackageDimensionsLength),
                ("幅(梱包)", self.PackageDimensionsWidth),
                ("画像", self.SmallImage) 
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
