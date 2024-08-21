from pymongo import MongoClient


def connectToDb(tenant):
    uri = "mongodb+srv://partha:AVyXZzEQhvBQCa8o@demo.xhcvolw.mongodb.net/"
    client = MongoClient(uri)
    db = client[tenant]

    return db


def findInvoiceByReferenceNumber(tenant, referenceNumber, skip):
    db = connectToDb(tenant)
    res = db.invoiceLineItem.aggregate(
        [
            {"$match": {"ReferenceNumber": referenceNumber}},
            {
                "$addFields": {
                    "ItemLineNumber": {
                        "$convert": {
                            "input": "$ItemLineNumber",
                            "to": "int",
                            "onError": None,
                            "onNull": None,
                        }
                    }
                }
            },
            {"$sort": {"ItemLineNumber": 1}},
            {"$skip": skip},
            {"$limit": 30},
        ]
    )
    print("res---->", res)
    return res


def findPaidDate(tenant, referenceNumber):
    db = connectToDb(tenant)
    res = db.collections.find_one({"invoiceId": referenceNumber})
    return res
