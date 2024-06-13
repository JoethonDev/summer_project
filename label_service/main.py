from fastapi import FastAPI, HTTPException
from utils import *
from models import LabelRequest


app = FastAPI()



# GET Request Methods
@app.get("/labels")
def get_labels():
    labels = collection.find({"parent_labels": {"$exists": False}})
    return [serialize(label) for label in labels]

@app.get("/labels/{label_id}")
def get_label_details(label_id: str):
    label = collection.find_one({"_id" : ObjectId(label_id)})
    if label :
        return serialize(label)
    return HTTPException(404, detail="Label is not found")

@app.get("/labels/{label_id}/recipes")
def get_recipes_by_label(label_id: str):
    label = collection.find_one({"_id" : ObjectId(label_id)})
    if label :
        label = serialize(label)
        recipes = extract_recipes(label) or {"message" : "No recipes under this label!"}
        return recipes
    return HTTPException(404, detail="Label is not found")

@app.get("/labels/{label_id}/sub-labels")
def get_sub_labels_by_label(label_id: str):
    label = collection.find_one({"_id" : ObjectId(label_id)})
    if label :
        label = serialize(label)
        sub_labels = extract_sub_labels(label) or {"message" : "No sub_labels under this label!"}
        # print(f"Sub_labels : {sub_labels}")
        return sub_labels
    return HTTPException(404, detail="Label is not found")

@app.get("/labels/{label_id}/statistics")
def get_label_stats(label_id: str):
    label = collection.find_one({"_id" : ObjectId(label_id)})
    if label :
        recipes = get_recipes_by_label(label_id)
        sub_labels = get_sub_labels_by_label(label_id)
        sub_labels_tree = count_sub_labels(sub_labels)
        label_stats = {
            "Label usage for recipes" : len(recipes),
            "Label usage as parent label" : sub_labels_tree
        }

        return label_stats
    return HTTPException(404, detail="Label is not found")


# POST Request Methods
@app.post("/labels")
def create_label(label: LabelRequest):
    label_record = collection.insert_one(dict(label))
    label_id = str(label_record.inserted_id)
    saved_label = get_label_details(label_id)
    return saved_label

@app.post("/labels/{label_id}/sub-labels")
def create_sub_label(label_id: str, label: LabelRequest):
    parent_label_record = collection.find_one({"_id" : ObjectId(label_id)})
    if not parent_label_record:
        return HTTPException(404, detail="Label is not found")
    
    sub_label = collection.insert_one(dict(label))
    sub_label_id = sub_label.inserted_id
    sub_label_record = collection.find_one({"_id" : sub_label_id})

    # Update records
    parent_label_record = insert_value(parent_label_record, "children_labels", str(sub_label_id))
    collection.update_one({"_id" : parent_label_record['_id']}, {"$set" : parent_label_record})

    sub_label_record = insert_value(sub_label_record, 'parent_labels', str(parent_label_record['_id']))
    collection.update_one({"_id" : sub_label_record['_id']}, {"$set" : sub_label_record})
    return get_label_details(sub_label_id)

# PUT Request Methods
@app.put("/labels/{label_id}")
def update_label(label_id: str, label: LabelRequest):
    label = dict(label)
    collection.update_one({"_id" : ObjectId(label_id)}, {'$set': label})
    return get_label_details(label_id)

# DELTE Request Methods
@app.delete("/labels/{label_id}")
def delete_label(label_id: str):
    label_record = get_label_details(label_id)
    sub_labels = get_sub_labels_by_label(label_id)
    for sub_label in sub_labels:
        delete_label(sub_label['id'])
    collection.delete_one({"_id" : ObjectId(label_id)})
    return label_record