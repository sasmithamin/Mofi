from bson import ObjectId

def serialize_mongo(data):
    if isinstance(data, dict):
        return {
            k: str(v) if isinstance(v, ObjectId) else v
            for k, v in data.items()
        }
    return data
