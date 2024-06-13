from pydantic import BaseModel
from typing import Optional

class CommentSchema(BaseModel):
    comment: str
    parent_comment: Optional[int]