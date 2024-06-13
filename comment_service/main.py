from fastapi import FastAPI, Depends, HTTPException
from database import SessionLocal, engine, Base
from models import *
from utils import *
from schema import CommentSchema
from sqlalchemy.orm import Session
from sqlalchemy import and_

app = FastAPI()

# Creating Tables
Base.metadata.create_all(engine)

# Preload records
# @app.on_event("startup")
# async def startup_event():
#     session = SessionLocal()
#     try:
#         # Create 10 comments (including sub-comments)
#         comments = [
#             Comments(comment="Parent comment 1", user=1, recipe=1),
#             Comments(comment="Parent comment 2", user=2, recipe=1),
#             Comments(comment="Parent comment 3", user=3, recipe=1),
#             Comments(comment="Parent comment 4", user=4, recipe=1),
#             Comments(comment="Parent comment 5", user=5, recipe=1),
#             Comments(comment="Sub-comment 1.1", user=6, recipe=1, parent_comment=1),
#             Comments(comment="Sub-comment 1.2", user=7, recipe=1, parent_comment=1),
#             Comments(comment="Sub-comment 2.1", user=8, recipe=1, parent_comment=2),
#             Comments(comment="Sub-comment 2.2", user=9, recipe=1, parent_comment=2),
#             Comments(comment="Sub-comment 3.1", user=10, recipe=1, parent_comment=3),
#         ]
#         session.add_all(comments)
#         session.commit()

#         # Add 5 likes to comments
#         likes = [
#             Comments_Likes(comment_id=1, user_id=1),
#             Comments_Likes(comment_id=2, user_id=2),
#             Comments_Likes(comment_id=3, user_id=3),
#             Comments_Likes(comment_id=4, user_id=4),
#             Comments_Likes(comment_id=5, user_id=5),
#         ]
#         session.add_all(likes)
#         session.commit()

#         # Optional: Output the preloaded comments
#         all_comments = session.query(Comments).all()
#         for comment in all_comments:
#             print(f"Preloaded comment: {comment.comment} (ID: {comment.id})")

#     except Exception as e:
#         session.rollback()
#         raise
#     finally:
#         session.close()



# dependency injection
def get_db():
    try :
        db = SessionLocal()
        yield db
    finally :
        db.close()

# Routes
@app.get("/health")
def health():
    return "Service is alive!"

@app.get("/recipes/{id}/comments")
def get_comments(id: int, db: Session = Depends(get_db)):
    # filter comments based on recipe and does not have a parent comment
    queries = get_comments_by_recipe(recipe_id=id, db=db)\
    .filter(Comments.parent_comment == None).all()

    # Seralizing comments
    comments = [comment.seralize() for comment in queries]
    return comments

@app.post("/recipes/{id}/comments")
def add_comment(id: int, comment: CommentSchema, db: Session = Depends(get_db)):
    # Check user is valid [JWT]

    # Make wraper if possible
    # Extract User Details
    user_id = 1

    # Build comment
    try :
        comment_record = create_comment(comment, id, user_id, db)
        return comment_record.seralize()

    except CreationCommentException as e:
        return HTTPException(400, detail=str(e))

@app.put("/recipes/{recipe_id}/comments/{comment_id}")
def update_comment(recipe_id: int, comment_id: int, comment: CommentSchema, db: Session = Depends(get_db)):
    # Check user is valid [JWT]

    # Make wraper if possible
    # Extract User Details
    user_id = 1

    # Build comment
    comment_record = get_comment(comment_id, recipe_id, db).first()

    if comment_record:
        if is_comment_owner(comment_record, user_id):
            comment_record.comment = comment.comment
            db.commit()
            return comment_record.seralize()
        
        return HTTPException(401, detail="Unauthorized action!")
    return HTTPException(404, detail="Comment is not found!")

@app.delete("/recipes/{recipe_id}/comments/{comment_id}")
def delete_comment(recipe_id: int, comment_id: int, db: Session = Depends(get_db)):
    # Check user is valid [JWT]

    # Make wraper if possible
    # Extract User Details
    user_id = 1

    # Build comment
    comment = get_comment(comment_id, recipe_id, db).first()

    if comment:
        if is_comment_owner(comment, user_id):
            db.delete(comment)
            db.commit()

            return comment.seralize()
        return HTTPException(401, detail="Unauthorized action!")
        
    return HTTPException(404, detail="Comment is not found!")

@app.post("/recipes/{recipe_id}/comments/{comment_id}/reply")
def reply_to_comment(recipe_id: int, comment_id: int, comment: CommentSchema, db: Session = Depends(get_db)):
    # Check user is valid [JWT]

    # Make wraper if possible
    # Extract User Details
    user_id = 1

    try :
        comment_record = create_comment(comment, recipe_id, user_id, db)
        # make it in another function if resused again
        parent_comment = get_comment(comment_id, recipe_id, db).first()
        if parent_comment:
            comment_record.parent_comment = parent_comment.id
            db.commit()

        return comment_record.seralize()

    except CreationCommentException as e:
        return HTTPException(400, detail=str(e))
    
@app.post("/recipes/{recipe_id}/comments/{comment_id}/like")
def like_comment(recipe_id: int, comment_id: int, db: Session = Depends(get_db)):
    # Check user is valid [JWT]

    # Make wraper if possible
    # Extract User Details
    user_id = 1

    comment_like_record = db.query(Comments_Likes).filter(and_(
        Comments_Likes.comment_id == comment_id,
        Comments_Likes.user_id == user_id
    )).first()
    comment_record = get_comment(comment_id=comment_id, recipe_id=recipe_id, db=db).first()
    if not comment_record:
        return HTTPException(404, "Comment is not found!")

    msg = "Like is added successfully"
    if comment_like_record:
        db.delete(comment_like_record)
        comment_record.likes -= 1
        msg = "Like is removed successfully"
        
    else:
        comment_like_record = Comments_Likes(comment_id=comment_id, user_id=user_id)
        db.add(comment_like_record)
        comment_record.likes += 1
    
    db.commit()

    return {"message" : msg}

