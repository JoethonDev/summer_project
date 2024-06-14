from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from motor.motor_asyncio import AsyncIOMotorCollection
from database import get_db
from schema import UpdateRecipe, DeleteRecipe
from CRUD import update_recipe as update_recipe_crud, delete_recipe as delete_recipe_crud, upload_image as upload_image_crud
from schema import Recipe, CreateRecipe, UpdateRecipe, DeleteRecipe
from CRUD import (
    create_recipe as create_recipe_crud,
    get_recipes as get_recipes_crud,
    get_recipe_by_id as get_recipe_by_id_crud
)

router = APIRouter()


@router.get("/recipes", response_model=List[Recipe])
async def get_recipes(
    db: AsyncIOMotorCollection = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by recipe name"),
    category: Optional[str] = Query(None, description="Filter by recipe category")
):
    filters = {}
    if name:
        filters['name'] = name
    if category:
        filters['category'] = category
    recipes = await get_recipes_crud(db, filters)
    return recipes

@router.post("/recipes", response_model=Recipe)
async def create_recipe(new_recipe: CreateRecipe, db: AsyncIOMotorCollection = Depends(get_db)):
    created_recipe = await create_recipe_crud(new_recipe.dict(), db)
    if not created_recipe:
        raise HTTPException(status_code=400, detail="Failed to create recipe")
    return created_recipe

@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str, db: AsyncIOMotorCollection = Depends(get_db)):
    recipe = await get_recipe_by_id_crud(recipe_id, db)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/recipe/{recipe_id}", response_model=UpdateRecipe)
async def update_recipe(recipe_id: str, update_recipe: UpdateRecipe, db: AsyncIOMotorCollection = Depends(get_db)):
    updated_recipe = await update_recipe_crud(recipe_id, update_recipe.model_dump(), db)
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated_recipe

@router.delete("/recipe/{recipe_id}", response_model=DeleteRecipe)
async def delete_recipe(recipe_id: str, db: AsyncIOMotorCollection = Depends(get_db)):
    deleted_recipe = await delete_recipe_crud(recipe_id, db)
    if not deleted_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return deleted_recipe


@router.post("/recipe/{recipe_id}")
async def upload_image_endpoint(recipe_id: str, file: UploadFile = File(...), db: AsyncIOMotorCollection = Depends(get_db)):
    try:
        image_recipe = await upload_image_crud(recipe_id, file, db)
        if not image_recipe:
            raise HTTPException(status_code=400, detail="Please send a message")
        return image_recipe
    except Exception as e:
        return {"detail": f"Failed to upload the image: {str(e)}"}