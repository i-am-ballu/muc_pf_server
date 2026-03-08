from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

class LoginRequest(BaseModel):
    email: str
    password: str
