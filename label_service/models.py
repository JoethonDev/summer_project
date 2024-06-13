from pydantic import BaseModel
from typing import Optional, List
from bson.objectid import ObjectId

class LabelRequest(BaseModel):
    name: str
    recipes : Optional[List[str]] = []
    children_labels : Optional[List[str]] = []

