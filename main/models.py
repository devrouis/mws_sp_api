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

import ast


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
    """??????????????????????????????."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """???????????????????????????????????????????????????"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(??????????????????????????????????????????)??????is_superuer(???????????????)???False???"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """??????????????????????????????is_staff???is_superuser???True???"""
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
        verbose_name='???', max_length=255, null=False, blank=False)
    first_name = models.CharField(
        verbose_name='???', max_length=255, null=True, blank=False)
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
        default=True, verbose_name='JAN??????????????????ASIN?????????')
    paid = models.BooleanField(default=True)

    is_staff = models.BooleanField(
        _('?????????'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('????????????'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    @property
    def username(self):
        """username?????????????????????
        ?????????????????????????????????username???????????????????????????????????????????????????
        ??????????????????????????????
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

@background(schedule=5)
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

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["attributes"]

    @property
    def Summaries(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["summaries"][0]

    @property
    def SalesRanks(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["salesRanks"][0]

    @property
    def ItemPackageDimensions(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["attributes"]["item_package_dimensions"][0]

    @property
    def ItemPackageWeight(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["attributes"]["item_package_weight"][0]

    @property
    def Images(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["images"][0]

    @property
    def NewProductsSummary(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[1]
        return data["body"]["payload"]["Summary"]

    @property
    def UsedProductsSummary(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None
        
        data = ast.literal_eval(self.get_matching_product_for_id_raw)[2]
        return data["body"]["payload"]["Summary"]

    @property
    def dbasin(self):
        if not self.get_matching_product_for_id_raw or self.get_matching_product_for_id_raw == '':
            return None

        data = ast.literal_eval(self.get_matching_product_for_id_raw)[0]
        return data["asin"]

    @property
    def dbjan(self):
        attributesets = self.AttributeSets
        try:
            if not attributesets:
                return None
            return attributesets["externally_assigned_product_identifier"][0]["value"]
        except KeyError:
            return None

    @property
    def Title(self):
        attributesets = self.AttributeSets
        if not attributesets:
            return None
        try:
            return attributesets["item_name"][0]["value"]
        except KeyError:
            return None
    
    @property
    def Publisher(self):
        summaries = self.Summaries
        if not summaries:
            return None
        try:
            return summaries["manafacture"]
        except KeyError:
            return None

    @property
    def PartNumber(self):
        summaries = self.Summaries
        if not summaries:
            return None
        try:
            return summaries["PartNumber"]
        except KeyError:
            return None

    @property
    def ProductGroup(self):
        summaries = self.Summaries
        if not summaries:
            return None
        try:
            return summaries["itemClassification"]
        except KeyError:
            return None

    @property
    def PackageDimensionsWeight(self):
        itemPackageWeight = self.ItemPackageWeight
        if not itemPackageWeight:
            return None
        try:
            return itemPackageWeight["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsHeight(self):
        itemPackageDimensions = self.ItemPackageDimensions
        if not itemPackageDimensions:
            return None
        try:
            return itemPackageDimensions["height"]["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsLength(self):
        itemPackageDimensions = self.ItemPackageDimensions
        if not itemPackageDimensions:
            return None
        try:
            return itemPackageDimensions["length"]["value"]
        except KeyError:
            return None

    @property
    def PackageDimensionsWidth(self):
        itemPackageDimensions = self.ItemPackageDimensions
        if not itemPackageDimensions:
            return None
        try:
            return itemPackageDimensions["width"]["value"]
        except KeyError:
            return None

    @property
    def SmallImage(self):
        images = self.Images
        if not images:
            return None
        try:
            return images["images"][0]["link"]
        except KeyError:
            return None

    @property
    def SalesRankingOneId(self):
        salesRanks = self.SalesRanks
        if not salesRanks:
            return None
        try:
            return salesRanks["classificationRanks"][0]["title"]
        except KeyError:
            return None
    
    @property
    def SalesRankingOneRank(self):
        salesRanks = self.SalesRanks
        if not salesRanks:
            return None
        try:
            return salesRanks["classificationRanks"][0]["rank"]
        except KeyError:
            return None

    @property
    def SalesRankingTwoId(self):
        salesRanks = self.SalesRanks
        if not salesRanks:
            return None
        try:
            return salesRanks["displayGroupRanks"][0]["title"]
        except KeyError:
            return None
    
    @property
    def SalesRankingTwoRank(self):
        salesRanks = self.SalesRanks
        if not salesRanks:
            return None
        try:
            return salesRanks["displayGroupRanks"][0]["rank"]
        except KeyError:
            return None
    
    @property
    def ListPriceAmount(self):
        newProductSummary = self.NewProductsSummary
        if not newProductSummary:
            return None
        try:
            return newProductSummary["ListPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPriceLandAmount(self):
        newProductSummary = self.NewProductsSummary
        if not newProductSummary:
            return None
        try:
            return newProductSummary["BuyBoxPrices"][0]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPriceShippingAmount(self):
        newProductSummary = self.NewProductsSummary
        if not newProductSummary:
            return None
        try:
            return newProductSummary["BuyBoxPrices"][0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def BuyBoxPricePointsNumber(self):
        newProductSummary = self.NewProductsSummary
        if not newProductSummary:
            return None
        try:
            return newProductSummary["BuyBoxPrices"][0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def NewProductLowestPrices(self):
        # if not self.NewProductsSummary["LowestPrices"] or self.NewProductsSummary["LowestPrices"] == '':
        #     return None
        try:
            return self.NewProductsSummary["LowestPrices"]
        except KeyError:
            return None
        
        
    @property
    def AmazonNewLowestLandPriceAmount(self):
        newProductLowestPrices = self.NewProductLowestPrices
        
        if not newProductLowestPrices:
            return None
        try:
            
            return newProductLowestPrices[0]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonNewLowestShippingAmount(self):
        newProductLowestPrices = self.NewProductLowestPrices
        if not newProductLowestPrices:
            return None
        try:
            return newProductLowestPrices[0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonNewLowestPointsNumber(self):
        newProductLowestPrices = self.NewProductLowestPrices
        if not newProductLowestPrices:
            return None
        try:
            return newProductLowestPrices[0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def AmazonOfferCount(self):
        newProductSummary = self.NewProductsSummary
        if not newProductSummary:
            return None
        try:
            return newProductSummary["NumberOfOffers"][0]["OfferCount"] 

        except KeyError:
            return None

    @property
    def MerchantNewProductLowestPrices(self):
        try:
            if len(self.NewProductsSummary["LowestPrices"]) < 2:
                return None
            return self.NewProductsSummary["LowestPrices"][1]
        except KeyError:
            return None
    
    @property
    def MerchantNewLowestLandPriceAmount(self):
        newProductLowestPrices = self.MerchantNewProductLowestPrices
        if not newProductLowestPrices:
            return None
        try:
            return newProductLowestPrices["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantNewLowestShippingAmount(self):
        newProductLowestPrices = self.MerchantNewProductLowestPrices
        if not newProductLowestPrices:
            return None
        try:
            return newProductLowestPrices["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantNewLowestPointsNumber(self):
        newProductLowestPrices = self.MerchantNewProductLowestPrices
        if not newProductLowestPrices:
            return None
        try:
            return newProductLowestPrices["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def MerchantOfferCount(self):
        newProductSummary = self.NewProductsSummary
        try:
            if len(newProductSummary["NumberOfOffers"]) < 2:
                return None
            return newProductSummary["NumberOfOffers"][1]["OfferCount"] 
        except KeyError:
            return None

    @property
    def AmazonUsedLowestLandPriceAmount(self):
        usedProductSummary = self.UsedProductsSummary
        if not usedProductSummary:
            return None
        try:
            return usedProductSummary["LowestPrices"][0]["LandedPrice"]["Amount"]
        except:
            return None
    
    @property
    def AmazonUsedLowestShippingAmount(self):
        usedProductSummary = self.UsedProductsSummary
        if not usedProductSummary:
            return None
        try:
            return usedProductSummary["LowestPrices"][0]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def AmazonUsedLowestPointsNumber(self):
        usedProductSummary = self.UsedProductsSummary
        if not usedProductSummary:
            return None
        try:
            return usedProductSummary["LowestPrices"][0]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def AmazonUsedOfferCount(self):
        usedProductSummary = self.UsedProductsSummary
        if not usedProductSummary:
            return None
        try:
            return usedProductSummary["NumberOfOffers"][0]["OfferCount"] 
        except KeyError:
            return None

    @property
    def MerchantUsedLowestLandPriceAmount(self):
        usedProductSummary = self.UsedProductsSummary
       
        try:
            if len(usedProductSummary["LowestPrices"]) < 2:
                return None
            return usedProductSummary["LowestPrices"][1]["LandedPrice"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedLowestShippingAmount(self):
        usedProductSummary = self.UsedProductsSummary
        try:
            if len(usedProductSummary["LowestPrices"]) < 2:
                return None
            return usedProductSummary["LowestPrices"][1]["Shipping"]["Amount"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedLowestPointsNumber(self):
        usedProductSummary = self.UsedProductsSummary
        try:
            if len(usedProductSummary["LowestPrices"]) < 2:
                return None
            return usedProductSummary["LowestPrices"][1]["Points"]["PointsNumber"]
        except KeyError:
            return None
    
    @property
    def MerchantUsedOfferCount(self):
        usedProductSummary = self.UsedProductsSummary
        try:
            if len(usedProductSummary["NumberOfOffers"]) < 2:
                return None
            return usedProductSummary["NumberOfOffers"][1]["OfferCount"] 
        except KeyError:
            return None

    CSV_HEADERS = [
        "ASIN",
        "JAN",
        "????????????",
        "????????????????????????",
        "??????",
        "??????????????????1",
        "???????????????1",
        "??????????????????2",
        "???????????????2",
        "????????????",
        # "ProductTypeName",	
        "??????",
        "BuyBox??????",
        "BuyBox??????",
        "BuyBox????????????",
        "Amazon???????????????",
        "Amazon????????????",
        "Amazon??????????????????",
        "Amazon?????????",
        "Merchant???????????????",
        "Merchant????????????",
        "Merchant??????????????????",
        "Merchant?????????",
        "Amazon???????????????",
        "Amazon????????????",
        "Amazon??????????????????",
        "Amazon?????????",
        "Merchant???????????????",
        "Merchant????????????",
        "Merchant??????????????????",
        "Merchant?????????",
        "????????????",	
        "??????(??????)",         
        "??????(??????)",       
        "???(??????)",
        "??????" 
    ]
    CSV_HEADERS_JAN = [
        "JAN",
        "ASIN",
        "????????????",
        "????????????????????????",
        "??????",
        "??????????????????1",
        "???????????????1",
        "??????????????????2",
        "???????????????2",
        "????????????",
        # "ProductTypeName",	
        "??????",
        "BuyBox??????",
        "BuyBox??????",
        "BuyBox????????????",
        "Amazon???????????????",
        "Amazon????????????",
        "Amazon??????????????????",
        "Amazon?????????",
        "Merchant???????????????",
        "Merchant????????????",
        "Merchant??????????????????",
        "Merchant?????????",
        "Amazon???????????????",
        "Amazon????????????",
        "Amazon??????????????????",
        "Amazon?????????",
        "Merchant???????????????",
        "Merchant????????????",
        "Merchant??????????????????",
        "Merchant?????????",
        "????????????",	
        "??????(??????)",         
        "??????(??????)",       
        "???(??????)",
        "??????" 
    ]

    @property
    def csv_columns(self):
        return [
                ("ASIN", self.dbasin),
                ("JAN", self.dbjan ),
                ("????????????", self.Title),
                ("????????????????????????", self.Publisher),
                ("??????", self.PartNumber),
                ("??????????????????1", self.SalesRankingOneId),
                ("???????????????1", self.SalesRankingOneRank),
                ("??????????????????2", self.SalesRankingTwoId),
                ("???????????????2", self.SalesRankingTwoRank),
                ("????????????", self.ProductGroup),
                # # ("ProductTypeName",	),
                ("??????", self.ListPriceAmount),
                ("BuyBox??????", self.BuyBoxPriceLandAmount),
                ("BuyBox??????", self.BuyBoxPriceShippingAmount),
                ("BuyBox????????????", self.BuyBoxPricePointsNumber),
                ("Amazon???????????????", self.AmazonNewLowestLandPriceAmount),
                ("Amazon????????????", self.AmazonNewLowestShippingAmount),
                ("Amazon??????????????????", self.AmazonNewLowestPointsNumber),
                ("Amazon?????????", self.AmazonOfferCount),
                ("Merchant???????????????", self.MerchantNewLowestLandPriceAmount),
                ("Merchant????????????", self.MerchantNewLowestShippingAmount),
                ("Merchant??????????????????", self.MerchantNewLowestPointsNumber),
                ("Merchant?????????", self.MerchantOfferCount),
                ("Amazon???????????????", self.AmazonUsedLowestLandPriceAmount),
                ("Amazon????????????", self.AmazonUsedLowestShippingAmount),
                ("Amazon??????????????????", self.AmazonUsedLowestPointsNumber),
                ("Amazon?????????", self.AmazonUsedOfferCount),
                ("Merchant???????????????", self.MerchantUsedLowestLandPriceAmount),
                ("Merchant????????????", self.MerchantUsedLowestShippingAmount),
                ("Merchant??????????????????", self.MerchantUsedLowestPointsNumber),
                ("Merchant?????????", self.MerchantUsedOfferCount),
                ("????????????", self.PackageDimensionsWeight),
                ("??????(??????)", self.PackageDimensionsHeight),
                ("??????(??????)", self.PackageDimensionsLength),
                ("???(??????)", self.PackageDimensionsWidth),
                ("??????", self.SmallImage) 
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
