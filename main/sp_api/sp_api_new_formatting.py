import json

def SP_API_NEW_FORMATTING(data):
    
    temp = {
            "payload": [
                {
                    "Identifiers":{
                        "MarketplaceASIN": {
                            "MarketplaceId": "", 
                            "ASIN": ""
                        }
                    }, 
                    "AttributeSets": [
                        {
                            "Format": [""], 
                            "AspectRatio": "", 
                            "Binding": "", 
                            "Brand": "", 
                            "ItemDimensions": {
                                "Height": {"value":"", "Units": ""}, 
                                "Length": {"value": "", "Units": ""}, 
                                "Width": {"value": "", "Units": ""}
                            }, 
                            "IsAdultProduct": "", 
                            "Label":"", 
                            "Languages": [{}], 
                            "ListPrice": {"Amount": "", "CurrencyCode": ""}, 
                            "Manufacturer":"", 
                            "NumberOfDiscs": 1, 
                            "NumberOfItems": 1, 
                            "PackageDimensions": {
                                "Height": {"value": "", "Units": ""}, 
                                "Length": {"value": "", "Units": ""}, 
                                "Width": {"value": "", "Units": ""}, 
                                "Weight": {"value": "", "Units": ""}
                            },
                            "ProductGroup": "", 
                            "ProductTypeName": "", 
                            "Publisher": "", 
                            "RegionCode": "", 
                            "ReleaseDate": "", 
                            "RunningTime": {"Units": "", "value": ""}, 
                            "SeikodoProductCode": "", 
                            "SmallImage": {
                                "URL": "", 
                                "Height": {"Units": "", "value": ""}, 
                                "Width": {"Units": "", "value": ""}
                            }, 
                            "Studio": "", 
                            "Title": ""
                        }
                    ], 
                    "Relationships": [], 
                    "SalesRankings": [
                        {
                            "ProductCategoryId": "", 
                            "Rank": ""
                        }, 
                        {
                            "ProductCategoryId": "", 
                            "Rank": ""
                        }
                    ]
                }, 
                {
                    "ASIN": "", 
                    "status": "", 
                    "ItemCondition": "", 
                    "Identifier": {
                        "MarketplaceId": "", 
                        "ItemCondition": "", 
                        "ASIN": ""
                    }, 
                    "Summary": {
                        "LowestPrices": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "LandedPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "ListingPrice": {"CurrencyCode": "", "Amount": ""}, 
                                "Shipping": {"CurrencyCode": "", "Amount": ""}, 
                                "Points": {"PointsNumber": ""}
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "LandedPrice": {
                                    "CurrencyCode": "", "Amount": ""
                                }, 
                                "ListingPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Shipping": {
                                    "CurrencyCode": "", "Amount": ""
                                }, 
                                "Points": {"PointsNumber": ""}
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "Merchant", 
                                "LandedPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "ListingPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Shipping": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Points": {
                                    "PointsNumber": ""
                                }
                            }
                        ], 
                        "BuyBoxPrices": [
                            {
                                "condition": "",
                                "LandedPrice": {
                                    "CurrencyCode": "",
                                    "Amount": ""
                                },
                                "ListingPrice": {
                                    "CurrencyCode": "",
                                    "Amount": ""
                                },
                                "Shipping": {
                                    "CurrencyCode": "",
                                    "Amount": ""
                                },
                                "Points": {
                                    "PointsNumber": ""
                                }
                            }
                        ],
                        "NumberOfOffers": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }
                        ], 
                        "BuyBoxEligibleOffers": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": ""
                            }
                        ], 
                        "SalesRankings": [
                            {
                                "ProductCategoryId": "", 
                                "Rank": ""
                            }, 
                            {
                                "ProductCategoryId": "", 
                                "Rank": ""
                            }
                        ], 
                        "ListPrice": {
                            "CurrencyCode": "", 
                            "Amount": ""
                        }, 
                        "TotalOfferCount": ""
                    }, 
                    "Offers": [
                        {
                            "Shipping": {
                                "CurrencyCode": "", 
                                "Amount": ""
                            }, 
                            "ListingPrice": {
                                "CurrencyCode": "", 
                                "Amount": ""
                            }, 
                            "ShippingTime": {
                                "maximumHours": "", 
                                "minimumHours": "", 
                                "availabilityType": ""
                            }, 
                            "SellerFeedbackRating": {
                                "FeedbackCount": "", 
                                "SellerPositiveFeedbackRating": ""
                            }, 
                            "ShipsFrom": {
                                "Country": ""
                            }, 
                            "PrimeInformation": {
                                "IsPrime": "", 
                                "IsNationalPrime": ""
                            }, 
                            "Points": {
                                "PointsNumber": ""
                            }, 
                            "SubCondition": "", 
                            "SellerId": "", 
                            "ConditionNotes": "",
                            "IsFeaturedMerchant": "", 
                            "IsBuyBoxWinner": "", 
                            "IsFulfilledByAmazon": ""
                        }
                    ], 
                    "marketplaceId": ""
                }, 
                {
                    "ASIN": "", 
                    "status": "", 
                    "ItemCondition": "", 
                    "Identifier": {
                        "MarketplaceId": "", 
                        "ItemCondition": "", 
                        "ASIN": ""
                    }, 
                    "Summary": {
                        "LowestPrices": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "LandedPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "ListingPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Shipping": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Points": {
                                    "PointsNumber": ""
                                }
                            }, 
                            {
                                "condition": "used", 
                                "fulfillmentChannel": "", 
                                "LandedPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "ListingPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Shipping": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Points": {
                                    "PointsNumber": ""
                                }
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "LandedPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "ListingPrice": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                }, 
                                "Shipping": {
                                    "CurrencyCode": "", 
                                    "Amount": ""
                                },
                                "Points": {
                                    "PointsNumber": 0
                                }
                            }
                        ], 
                        "NumberOfOffers": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            }
                        ], 
                        "BuyBoxEligibleOffers": [
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            },
                            {
                                "condition": "",
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            }, 
                            {
                                "condition": "", 
                                "fulfillmentChannel": "", 
                                "OfferCount": 0
                            }
                        ], 
                        "SalesRankings": [
                            {
                                "ProductCategoryId": "", 
                                "Rank": 0
                            }, 
                            {
                                "ProductCategoryId": "", 
                                "Rank": 0
                            }
                        ], 
                        "ListPrice": {
                            "CurrencyCode": "JPY", 
                            "Amount": 0
                        }, 
                        "TotalOfferCount": 0
                    }, 
                    "Offers": [
                        {
                            "Shipping": {
                                "CurrencyCode": "", 
                                "Amount": ""
                            }, 
                            "ListingPrice": {
                                "CurrencyCode": "", 
                                "Amount": ""
                            }, 
                            "ShippingTime": {
                                "maximumHours": "", 
                                "minimumHours": "", 
                                "availabilityType": ""
                            }, 
                            "SellerFeedbackRating": {
                                "FeedbackCount": "", 
                                "SellerPositiveFeedbackRating": ""
                            }, 
                            "ShipsFrom": {
                                "Country": ""
                            }, 
                            "PrimeInformation": {
                                "IsPrime": "", 
                                "IsNationalPrime": ""
                            },
                            "Points": {
                                "PointsNumber": ""
                            }, 
                            "SubCondition": "", 
                            "SellerId": "", 
                            "ConditionNotes": "", 
                            "IsFeaturedMerchant": "", 
                            "IsBuyBoxWinner": "", 
                            "IsFulfilledByAmazon": ""
                        }, 
                    ], 
                    "marketplaceId": ""
                }
            ]
        }

    try:
        MarketplaceASIN = data["payload"][0]["Identifiers"]["MarketplaceASIN"]["MarketplaceId"]
    except:
        MarketplaceASIN = ""
    temp["payload"][0]["Identifiers"]["MarketplaceASIN"]["MarketplaceId"] = MarketplaceASIN

    try:
        ASIN = data["payload"][0]["Identifiers"]["MarketplaceASIN"]["ASIN"]
    except:
        ASIN = ""
    temp["payload"][0]["Identifiers"]["MarketplaceASIN"]["ASIN"] = ASIN

    
    try:
        Title = data["payload"][0]["AttributeSets"][0]["Title"]
    except:
        Title = ""

    temp["payload"][0]["AttributeSets"][0]["Title"] = Title

    try:
        Publisher = data["payload"][0]["AttributeSets"][0]["Publisher"]
    except:
        Publisher = ""
    temp["payload"][0]["AttributeSets"][0]["Publisher"] = Publisher

    try:
        PartNumber = data["payload"][0]["AttributeSets"][0]["PartNumber"]
    except:
        PartNumber = ""
    temp["payload"][0]["AttributeSets"][0]["PartNumber"] = PartNumber
    
    try:
        SalesRankingOneId = data["payload"][1]["Summary"]["SalesRankings"][0]["ProductCategoryId"]
    except:
        SalesRankingOneId = ""
    temp["payload"][1]["Summary"]["SalesRankings"][0]["ProductCategoryId"] = SalesRankingOneId
    
    try:
        SalesRankingOneRank = data["payload"][1]["Summary"]["SalesRankings"][0]["Rank"]
    except:
        SalesRankingOneRank = ""
    temp["payload"][1]["Summary"]["SalesRankings"][0]["Rank"] = SalesRankingOneRank
    
    try:
        SalesRankingTwoId = data["payload"][1]["Summary"]["SalesRankings"][1]["ProductCategoryId"]
    except:
        SalesRankingTwoId = ""
    temp["payload"][1]["Summary"]["SalesRankings"][1]["ProductCategoryId"] = SalesRankingTwoId
    
    try:
        SalesRankingTwoRank = data["payload"][1]["Summary"]["SalesRankings"][1]["Rank"]
    except:
        SalesRankingTwoRank = ""
    temp["payload"][1]["Summary"]["SalesRankings"][1]["Rank"] = SalesRankingTwoRank
    
    try:
        ProductGroup = data["payload"][0]["AttributeSets"][0]["ProductGroup"]
    except:
        ProductGroup = ""
    temp["payload"][0]["AttributeSets"][0]["ProductGroup"] = ProductGroup
    
    try:
        ListPriceAmount = data["payload"][1]["Summary"]["ListPrice"]["Amount"]
    except:
        ListPriceAmount = ""
    temp["payload"][1]["Summary"]["ListPrice"]["Amount"] = ListPriceAmount
    
    try:
        BuyBoxPriceLandAmount = data["payload"][1]["Summary"]["BuyBoxPrices"][0]["LandedPrice"]["Amount"]
    except:
        BuyBoxPriceLandAmount = ""
    temp["payload"][1]["Summary"]["BuyBoxPrices"][0]["LandedPrice"]["Amount"] = BuyBoxPriceLandAmount
    
    try:
        BuyBoxPriceShippingAmount = data["payload"][1]["Summary"]["BuyBoxPrices"][0]["Shipping"]["Amount"]
    except:
        BuyBoxPriceShippingAmount = ""
    temp["payload"][1]["Summary"]["BuyBoxPrices"][0]["Shipping"]["Amount"] = BuyBoxPriceShippingAmount
    
    try:
        BuyBoxPricePointsNumber = data["payload"][1]["Summary"]["BuyBoxPrices"][0]["Points"]["PointsNumber"]
    except:
        BuyBoxPricePointsNumber = ""
    temp["payload"][1]["Summary"]["BuyBoxPrices"][0]["Points"]["PointsNumber"] = BuyBoxPricePointsNumber
    
    try:
        AmazonNewLowestLandPriceAmount = data["payload"][1]["Summary"]["LowestPrices"][0]["LandedPrice"]["Amount"]
    except:
        AmazonNewLowestLandPriceAmount = ""
    temp["payload"][1]["Summary"]["LowestPrices"][0]["LandedPrice"]["Amount"] = AmazonNewLowestLandPriceAmount
    
    try:
        AmazonNewLowestShippingAmount = data["payload"][1]["Summary"]["LowestPrices"][0]["Shipping"]["Amount"]
    except:
        AmazonNewLowestShippingAmount = ""
    temp["payload"][1]["Summary"]["LowestPrices"][0]["Shipping"]["Amount"] = AmazonNewLowestShippingAmount
    
    try:
        AmazonNewLowestPointsNumber = data["payload"][1]["Summary"]["LowestPrices"][0]["Points"]["PointsNumber"]
    except:
        AmazonNewLowestPointsNumber = ""
    temp["payload"][1]["Summary"]["LowestPrices"][0]["Points"]["PointsNumber"] = AmazonNewLowestPointsNumber
    
    try:
        AmazonOfferCount = data["payload"][1]["Summary"]["NumberOfOffers"][0]["OfferCount"] 
    except:
        AmazonOfferCount = ""
    temp["payload"][1]["Summary"]["NumberOfOffers"][0]["OfferCount"]  = AmazonOfferCount
    
    try:
        MerchantNewLowestLandPriceAmount = data["payload"][1]["Summary"]["LowestPrices"][1]["LandedPrice"]["Amount"]
    except:
        MerchantNewLowestLandPriceAmount = ""
    temp["payload"][1]["Summary"]["LowestPrices"][1]["LandedPrice"]["Amount"] = MerchantNewLowestLandPriceAmount
    
    try:
        MerchantNewLowestShippingAmount = data["payload"][1]["Summary"]["LowestPrices"][1]["Shipping"]["Amount"]
    except:
        MerchantNewLowestShippingAmount = ""
    temp["payload"][1]["Summary"]["LowestPrices"][1]["Shipping"]["Amount"] = MerchantNewLowestShippingAmount
    
    try:
        MerchantNewLowestPointsNumber = data["payload"][1]["Summary"]["LowestPrices"][1]["Points"]["PointsNumber"]
    except:
        MerchantNewLowestPointsNumber = ""
    temp["payload"][1]["Summary"]["LowestPrices"][1]["Points"]["PointsNumber"] = MerchantNewLowestPointsNumber
    
    try:
        MerchantOfferCount = data["payload"][1]["Summary"]["NumberOfOffers"][1]["OfferCount"] 
    except:
        MerchantOfferCount = ""
    temp["payload"][1]["Summary"]["NumberOfOffers"][1]["OfferCount"]  = MerchantOfferCount
    
    try:
        AmazonUsedLowestLandPriceAmount = data["payload"][2]["Summary"]["LowestPrices"][0]["LandedPrice"]["Amount"]
    except:
        AmazonUsedLowestLandPriceAmount = ""
    temp["payload"][2]["Summary"]["LowestPrices"][0]["LandedPrice"]["Amount"] = AmazonUsedLowestLandPriceAmount
    
    try:
        AmazonUsedLowestShippingAmount = data["payload"][2]["Summary"]["LowestPrices"][0]["Shipping"]["Amount"]
    except:
        AmazonUsedLowestShippingAmount = ""
    temp["payload"][2]["Summary"]["LowestPrices"][0]["Shipping"]["Amount"] = AmazonUsedLowestShippingAmount
    
    try:
        AmazonUsedLowestPointsNumber = data["payload"][2]["Summary"]["LowestPrices"][0]["Points"]["PointsNumber"]
    except:
        AmazonUsedLowestPointsNumber = ""
    temp["payload"][2]["Summary"]["LowestPrices"][0]["Points"]["PointsNumber"] = AmazonUsedLowestPointsNumber
    
    try:
        AmazonUsedOfferCount = data["payload"][2]["Summary"]["NumberOfOffers"][0]["OfferCount"] 
    except:
        AmazonUsedOfferCount = ""
    temp["payload"][2]["Summary"]["NumberOfOffers"][0]["OfferCount"]  = AmazonUsedOfferCount
    
    try:
        MerchantUsedLowestLandPriceAmount = data["payload"][2]["Summary"]["LowestPrices"][1]["LandedPrice"]["Amount"]
    except:
        MerchantUsedLowestLandPriceAmount = ""
    temp["payload"][2]["Summary"]["LowestPrices"][1]["LandedPrice"]["Amount"] = MerchantUsedLowestLandPriceAmount
    
    try:
        MerchantUsedLowestShippingAmount = data["payload"][2]["Summary"]["LowestPrices"][1]["Shipping"]["Amount"]
    except:
        MerchantUsedLowestShippingAmount = ""
    temp["payload"][2]["Summary"]["LowestPrices"][1]["Shipping"]["Amount"] = MerchantUsedLowestShippingAmount
    
    try:
        MerchantUsedLowestPointsNumber = data["payload"][2]["Summary"]["LowestPrices"][1]["Points"]["PointsNumber"]
    except:
        MerchantUsedLowestPointsNumber = ""
    temp["payload"][2]["Summary"]["LowestPrices"][1]["Points"]["PointsNumber"] = MerchantUsedLowestPointsNumber
    
    try:
        MerchantUsedOfferCount = data["payload"][2]["Summary"]["NumberOfOffers"][1]["OfferCount"] 
    except:
        MerchantUsedOfferCount = ""
    temp["payload"][2]["Summary"]["NumberOfOffers"][1]["OfferCount"]  = MerchantUsedOfferCount

    try:
        PackageDimensionsWeight = data["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Weight"]["value"]
    except:
        PackageDimensionsWeight = ""
    temp["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Weight"]["value"] = PackageDimensionsWeight

    try:
        PackageDimensionsHeight = data["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Height"]["value"]
    except:
        PackageDimensionsHeight = ""
    temp["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Height"]["value"] = PackageDimensionsHeight

    try:
        PackageDimensionsLength = data["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Length"]["value"]
    except:
        PackageDimensionsLength = ""
    temp["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Length"]["value"] = PackageDimensionsLength

    try:
        PackageDimensionsWidth = data["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Width"]["value"]
    except:
        PackageDimensionsWidth = ""
    temp["payload"][0]["AttributeSets"][0]["PackageDimensions"]["Width"]["value"] = PackageDimensionsWidth

    try:
        SmallImage = data["payload"][0]["AttributeSets"][0]["SmallImage"]["URL"]
    except:
        SmallImage = ""
    temp["payload"][0]["AttributeSets"][0]["SmallImage"]["URL"] = SmallImage

    return temp