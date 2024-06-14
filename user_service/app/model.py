from pydantic import BaseModel, Field, EmailStr

class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserReturnSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)