from sqlalchemy import Column, PrimaryKeyConstraint, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement='auto')
    comment = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    user = Column(Integer, nullable=False)
    recipe = Column(Integer, nullable=False)
    parent_comment = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    # relation to children
    children_comments = relationship("Comments", cascade="delete")

    def __init__(self, comment, user, recipe, parent_comment = None):
        self.comment = comment
        self.recipe = recipe
        self.user = user
        self.parent_comment = parent_comment

    def get_children(self):
        children = []
        for child in self.children_comments:
            children.append(child.seralize())
        return children

    def seralize(self):
        return {
            "id" : self.id,
            "comment" : self.comment,
            "likes" : self.likes,
            "user" : self.user,
            "recipe" : self.recipe,
            "sub_comments" : self.get_children()
        }


class Comments_Likes(Base):
    __tablename__ = "comments_like"

    comment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint(
            comment_id,
            user_id),
        {})