def serialize_mongo(doc):
    if not doc:
        return doc

    if isinstance(doc, list):
        return [serialize_mongo(d) for d in doc]

    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
