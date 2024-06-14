from fastapi import FastAPI, Body, Depends, HTTPException
from app.model import UserSchema, UserLoginSchema, UserReturnSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from app.dbUser import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://root:admin@localhost:3306/user_service')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
app = FastAPI()

@app.post("/register", tags=["user"])
def create_user(user: UserSchema = Body(...)):
        with Session() as session:
                existing_user = session.query(User).filter(User.email == user.email.lower()).first()
                if existing_user:
                        raise HTTPException(status_code=400, detail="Email already registered")
                new_user = User(email=user.email.lower(), password=user.password, fullname=user.fullname)
                try:
                        session.add(new_user)
                        session.commit()
                except Exception as e:
                        session.rollback()
                        raise HTTPException(status_code=500, detail=f"Failed to register user due to {e}")
                return {
                    'token': signJWT(new_user.id),
                    'user_id': new_user.id,
                }

@app.post("/login", tags=["user"])
def user_login(user: UserLoginSchema = Body(...)):
        with Session() as session:
                existing_user = session.query(User).filter(User.email == user.email.lower()).first()
                if existing_user and existing_user.password == user.password:
                        return {
                            'token': signJWT(existing_user.id),
                            'user_id': existing_user.id,
                        }
        raise HTTPException(status_code=401, detail="Incorrect email or password")

@app.get("/users/{user_id}", dependencies=[Depends(JWTBearer())], tags=["user"])
def get_user(user_id: str, token_data: dict = Depends(JWTBearer())):
        if user_id != token_data.get("user_id"):
                raise HTTPException(status_code=403, detail="Not authorized to access this user data.")
        with Session() as session:
                existing_user = session.query(User).filter(User.id == user_id).first()
                if existing_user:
                        return UserReturnSchema(fullname=existing_user.fullname, email=existing_user.email)
        raise HTTPException(status_code=404, detail="User not found")
