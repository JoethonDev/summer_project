from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Recipe(BaseModel):
    id: str
    name: str
    category: str
    ingredients: List[str]
    instructions: str

class CreateRecipe(BaseModel):
    name: str
    category: str
    ingredients: List[str]
    instructions: str

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {'type': 'string'}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UpdateRecipe(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class DeleteRecipe(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
