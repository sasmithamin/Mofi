from bson import ObjectId
from datetime import datetime

def serialize_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]

    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_dict[key] = serialize_mongo(value)
        return new_dict

    return obj
