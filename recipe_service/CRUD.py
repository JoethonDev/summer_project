from typing import Any, Dict, List
from bson import ObjectId
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException, UploadFile
import uuid
from img import resize_image


async def get_recipes(db: AsyncIOMotorCollection, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    recipes_cursor = db.recipes.find(filters)
    recipes = await recipes_cursor.to_list(length=100)
    return recipes

async def get_recipe_by_id(recipe_id: str, db: AsyncIOMotorCollection) -> Dict[str, Any]:
    recipe = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return recipe

async def create_recipe(recipe_data: Dict[str, Any], db: AsyncIOMotorCollection) -> Dict[str, Any]:
    result = await db.recipes.insert_one(recipe_data)
    recipe_data['_id'] = str(result.inserted_id)
    return recipe_data


async def update_recipe(recipe_id: str, update_data: Dict[str, Any], db: AsyncIOMotorCollection) -> object:
    recipe_data = {key: value for key, value in update_data.items() if value is not None}
    result = await db.update_one({"_id": ObjectId(recipe_id)}, {"$set": recipe_data})

    if result.matched_count == 0:
        return None

    updated_recipe = await db.find_one({"_id": ObjectId(recipe_id)})
    return updated_recipe

async def delete_recipe(recipe_id: str, db: AsyncIOMotorCollection) -> object:
    result = await db.delete_one({"_id": ObjectId(recipe_id)})

    if result.deleted_count == 0:
        return None
    return {"_id": recipe_id}


async def upload_image(recipe_id: str, file: UploadFile, collection):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File is not an image")

    resized_image = await resize_image(file)

    # Unique name for image like user ID
    filename = f"{uuid.uuid4()}.jpg"

    import os
    os.makedirs("images", exist_ok=True)

    with open(f"images/{filename}", "wb") as f:
        f.write(resized_image.getvalue())

    await collection.update_one(
        {"_id": ObjectId(recipe_id)},
        {"$set": {"image_path": filename}}
    )

    return JSONResponse(status_code=200, content={"message": "Image uploaded successfully", "filename": filename})
