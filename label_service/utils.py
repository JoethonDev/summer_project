from database import collection
from bson import ObjectId

def get_label_record(label_id):
    label_record = collection.find_one({"_id" : ObjectId(label_id)})
    if not label_record:
        return HTTPException(404, detail="Label is not found")
    return label_record

def extract_sub_labels(record):
    sub_labels_list = []
    if "children_labels" in record:
        sub_labels = record['children_labels']
        for label in sub_labels :
            saved_record = collection.find_one({"_id" : ObjectId(label)})
            saved_record['children_labels'] = extract_sub_labels(saved_record)
            sub_labels_list.append(serialize(saved_record))

    return sub_labels_list

def extract_recipes(record):
    recipes = record['recipes']

    sub_labels = extract_sub_labels(record)
    for label in sub_labels :
        recipes += label['recipes']

    return recipes


def count_sub_labels(sub_labels, level: int = 1):
    # To be Fixed!
    # Basic condition no sub_labels
    level_no = {
        "level" : level,
        "children_labels_count" : len(sub_labels)
    }

    next_level_data = {
        "level" : level + 1,
        "children_labels_count" : 0
    }
    for label in sub_labels:
        next_level = count_sub_labels(label['children_labels'], level + 1)
        next_level_data["children_labels_count"] += next_level['children_labels_count']

    if next_level_data["children_labels_count"]:
        level_no['next_level'] = next_level_data

    return level_no

def insert_value(record, key, value):
    if key in record:
        record[key] += [value]
    else:
        record[key] = [value]
    return record

def serialize(record):
        id = str(record['_id'])
        del record['_id']

        return {
            "id" : id,
            **record
        }

