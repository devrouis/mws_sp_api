import os
from main.models import ScrapeRequest, ScrapeRequestResult
from rest_framework import serializers
import json

class JSONSerializerField(serializers.Field):
  def to_representation(self, value):
    return json.loads(value)

class ScrapeResultSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = ScrapeRequestResult
    fields = [
      'asin',
      'jan',
      'Title',
      'Publisher',
      'PartNumber',
      'SalesRankings',
      'Binding',
      'ReleaseDate',
      'ListPriceValue',
      'ListPriceCurrency',
      'LandedPriceValue',
      'LandedPriceCurrency',
      'ShippingValue',
      'ShippingCurrency',
      'PointsValue',
      'PointsCurrency',
      'OfferListingCountNew',
      'LowestOfferListingNewPriceValue',
      'LowestOfferListingNewPriceCurrency',
      'LowestOfferListingNewShippingValue',
      'LowestOfferListingNewShippingCurrency',
      'LowestOfferListingNewPointsValue',
      'LowestOfferListingNewPointsCurrency',
      'OfferListingCountUsed',
      'LowestOfferListingUsedPriceValue',
      'LowestOfferListingUsedPriceCurrency',
      'LowestOfferListingUsedShippingValue',
      'LowestOfferListingUsedShippingCurrency',
      'LowestOfferListingUsedPointsValue',
      'LowestOfferListingUsedPointsCurrency',
      'WeightValue',
      'WeightUnit',
      'HeightValue',
      'HeightUnit',
      'LengthValue',
      'LengthUnit',
      'WidthValue',
      'WidthUnit',
    ]
  
class ScrapeRequestSerializer(serializers.ModelSerializer):
  results = ScrapeResultSerializer(many = True)

  class Meta:
    model = ScrapeRequest
    fields = ['results', 'requested_at', 'status_text', 'error']
