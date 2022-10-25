import json

def SP_ASIN_FORMATTING(res):
    
    temp = {
            "Id":{
                "value":""
            },
            "IdType":{
                "value":""
            },
            "status":{
                "value":"Success"
            },
            "Products":{
                "Product":{
                    "Identifiers":{
                        "MarketplaceASIN":{
                        "MarketplaceId":{
                            "value":""
                        },
                        "ASIN":{
                            "value":""
                        }
                        }
                    },
                    "AttributeSets":{
                        "ItemAttributes":{
                        "lang":{
                            "value":"ja-JP"
                        },
                        "Binding":{
                            "value":""
                        },
                        "Brand":{
                            "value":"任天堂"
                        },
                        "CEROAgeRating":{
                            "value":"全年齢対象"
                        },
                        "ESRBAgeRating":{
                            "value":"Everyone"
                        },
                        "Genre":{
                            "value":"ゲーム"
                        },
                        "ItemDimensions":{
                            "Height":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Length":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Width":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Weight":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            }
                        },
                        "IsAdultProduct":{
                            "value":""
                        },
                        "Label":{
                            "value":""
                        },
                        "ListPrice":{
                            "Amount":{
                                "value":""
                            },
                            "CurrencyCode":{
                                "value":""
                            }
                        },
                        "Manufacturer":{
                            "value":""
                        },
                        "Model":{
                            "value":""
                        },
                        "PackageDimensions":{
                            "Height":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Length":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Width":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            },
                            "Weight":{
                                "value":"",
                                "Units":{
                                    "value":""
                                }
                            }
                        },
                        "PackageQuantity":{
                            "value":"1"
                        },
                        "PartNumber":{
                            "value":""
                        },
                        "PegiRating":{
                            "value":""
                        },
                        "Platform":{
                            "value":""
                        },
                        "ProductGroup":{
                            "value":""
                        },
                        "ProductTypeName":{
                            "value":""
                        },
                        "Publisher":{
                            "value":""
                        },
                        "ReleaseDate":{
                            "value":""
                        },
                        "Size":{
                            "value":""
                        },
                        "SmallImage":{
                            "URL":{
                                "value":"https://m.media-amazon.com/images/I/51l2xg5wiDL._SL75_.jpg"
                            },
                            "Height":{
                                "value":"75",
                                "Units":{
                                    "value":"pixels"
                                }
                            },
                            "Width":{
                                "value":"75",
                                "Units":{
                                    "value":"pixels"
                                }
                            }
                        },
                        "Studio":{
                            "value":""
                        },
                        "Title":{
                            "value":""
                        }
                        }
                    },
                    "Relationships":{
                        
                    },
                    "SalesRankings":{
                        "SalesRank":[
                        {
                            "ProductCategoryId":{
                                "value":""
                            },
                            "Rank":{
                                "value":"1495"
                            }
                        },
                        {
                            "ProductCategoryId":{
                                "value":""
                            },
                            "Rank":{
                                "value":""
                            }
                        }
                        ]
                    }
                }
            }
            }

    #---------Identifiers start
    try:
        MarketplaceId = res["payload"]["Identifiers"]["MarketplaceASIN"]["MarketplaceId"]
    except:
        MarketplaceId = ""

    temp["Products"]["Product"]["Identifiers"]["MarketplaceASIN"]["MarketplaceId"]["value"] = MarketplaceId

    try:
        ASIN = res["payload"]["Identifiers"]["MarketplaceASIN"]["ASIN"]
    except:
        ASIN = ""

    temp["Products"]["Product"]["Identifiers"]["MarketplaceASIN"]["ASIN"]["value"] = ASIN

    #---------Identifiers end

    #---------AttributeSets start

    try:
        Binding = res["payload"]["AttributeSets"][0]["Binding"]
    except:
        Binding = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Binding"]["value"] = Binding

    try:
        Brand = res["payload"]["AttributeSets"][0]["Brand"]
    except:
        Brand = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Brand"]["value"] = Brand

        #---------ItemDimensions start
    try:
        Height = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Height']['value']
    except:
        Height = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Height"]["value"] = Height

    try:
        Units = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Height']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Height"]["Units"]["value"] = Units

    try:
        Length = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Length']['value']
    except:
        Length = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Length"]["value"] = Length

    try:
        Units = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Length']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Length"]["Units"]["value"] = Units

    try:
        Width = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Width']['value']
    except:
        Width = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Width"]["value"] = Width

    try:
        Units = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Width']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Width"]["Units"]["value"] = Units


    try:
        Weight = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Weight']['value']
    except:
        Weight = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Weight"]["value"] = Weight

    try:
        Units = res["payload"]["AttributeSets"][0]["ItemDimensions"]['Weight']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ItemDimensions"]["Weight"]["Units"]["value"] = Units

        #---------ItemDimensions end

    try:
        Label = res["payload"]["AttributeSets"][0]["Label"]
    except:
        Label = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Label"]["value"] = Label

    try:
        ListPriceAmount = res["payload"]["AttributeSets"][0]["ListPrice"]["Amount"]
    except:
        ListPriceAmount = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ListPrice"]["Amount"]["value"] = ListPriceAmount

    try:
        ListPriceCurrencyCode = res["payload"]["AttributeSets"][0]["ListPrice"]["CurrencyCode"]
    except:
        ListPriceCurrencyCode = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ListPrice"]["CurrencyCode"]["value"] = ListPriceCurrencyCode

    try:
        Manufacturer = res["payload"]["AttributeSets"][0]["Manufacturer"]
    except:
        Manufacturer = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Manufacturer"]["value"] = Manufacturer

    try:
        Model = res["payload"]["AttributeSets"][0]["Model"]
    except:
        Model = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Model"]["value"] = Model

        #------------PackageDimensions start
    try:
        Height = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Height']['value']
    except:
        Height = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Height"]["value"] = Height

    try:
        Units = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Height']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Height"]["Units"]["value"] = Units

    try:
        Length = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Length']['value']
    except:
        Length = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Length"]["value"] = Length

    try:
        Units = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Length']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Length"]["Units"]["value"] = Units

    try:
        Width = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Width']['value']
    except:
        Width = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Width"]["value"] = Width

    try:
        Units = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Width']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Width"]["Units"]["value"] = Units

    try:
        Weight = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Weight']['value']
    except:
        Weight = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Weight"]["value"] = Weight

    try:
        Units = res["payload"]["AttributeSets"][0]["PackageDimensions"]['Weight']['Units']
    except:
        Units = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageDimensions"]["Weight"]["Units"]["value"] = Units
        #------------PackageDimensions end

    try:
        PackageQuantity = res["payload"]["AttributeSets"][0]["PackageQuantity"]
    except:
        PackageQuantity = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PackageQuantity"]["value"] = PackageQuantity

    try:
        PartNumber = res["payload"]["AttributeSets"][0]["PartNumber"]
    except:
        PartNumber = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PartNumber"]["value"] = PartNumber

    try:
        PegiRating = res["payload"]["AttributeSets"][0]["PegiRating"]
    except:
        PegiRating = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["PegiRating"]["value"] = PegiRating

    try:
        Platform = res["payload"]["AttributeSets"][0]["Platform"]
    except:
        Platform = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Platform"]["value"] = Platform

    try:
        ProductGroup = res["payload"]["AttributeSets"][0]["ProductGroup"]
    except:
        ProductGroup = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ProductGroup"]["value"] = ProductGroup

    try:
        ProductTypeName = res["payload"]["AttributeSets"][0]["ProductTypeName"]
    except:
        ProductTypeName = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["ProductTypeName"]["value"] = ProductTypeName

    try:
        Publisher = res["payload"]["AttributeSets"][0]["Publisher"]
    except:
        Publisher = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Publisher"]["value"] = Publisher

    try:
        Size = res["payload"]["AttributeSets"][0]["Size"]
    except:
        Size = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Size"]["value"] = Size

    try:
        Studio = res["payload"]["AttributeSets"][0]["Studio"]
    except:
        Studio = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Studio"]["value"] = Studio

    try:
        Title = res["payload"]["AttributeSets"][0]["Title"]
    except:
        Title = ""

    temp["Products"]["Product"]["AttributeSets"]["ItemAttributes"]["Title"]["value"] = Title

    #----------SalesRankings
    try:
        productcategoryId1 = res["payload"]["SalesRankings"][0]["ProductCategoryId"]
    except:
        productcategoryId1 = ""

    temp["Products"]["Product"]["SalesRankings"]["SalesRank"][0]["ProductCategoryId"]["value"] = productcategoryId1

    try:
        Rank1 = res["payload"]["SalesRankings"][0]["Rank"]
    except:
        Rank1 = ""

    temp["Products"]["Product"]["SalesRankings"]["SalesRank"][0]["Rank"]["value"] = Rank1

    try:
        productcategoryId2 = res["payload"]["SalesRankings"][1]["ProductCategoryId"]
    except:
        productcategoryId2 = ""

    temp["Products"]["Product"]["SalesRankings"]["SalesRank"][1]["ProductCategoryId"]["value"] = productcategoryId2

    try:
        Rank1 = res["payload"]["SalesRankings"][1]["Rank"]
    except:
        Rank1 = ""

    temp["Products"]["Product"]["SalesRankings"]["SalesRank"][1]["Rank"]["value"] = Rank1

    return temp


