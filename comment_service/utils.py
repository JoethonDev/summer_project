from models import *
from schema import CommentSchema

class CreationCommentException(Exception):
    def __init__(self):
        super().__init__("Comment can not be created! try again later")

# functions
def get_comments_by_recipe(recipe_id: int, db):
    comments = db.query(Comments).filter(Comments.recipe == recipe_id)
    return comments

def get_comment(comment_id: int, recipe_id: int, db):
    comments = get_comments_by_recipe(recipe_id, db)
    comment = None
    if comments:
        comment = comments.filter(Comments.id == comment_id)
    
    return comment

def is_comment_owner(comment: Comments, user_id: int):
    return comment.user == user_id

def create_comment(comment: CommentSchema, recipe_id: int, user_id: int, db):
    try:
        comment_record = Comments(comment=comment.comment, user=user_id, recipe=recipe_id)
        db.add(comment_record)
        db.commit()
        return comment_record
    except Exception as e:
        db.rollback()
        raise CreationCommentException
