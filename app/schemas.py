from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class BCIDataBase(BaseModel):
    timestamp: datetime
    channel_1: float
    channel_2: float
    channel_3: float
    channel_4: float

class BCIDataCreate(BCIDataBase):
    pass

class BCIData(BCIDataBase):
    id: int
    session_id: int

    class Config:
        orm_mode = True

class BCISessionBase(BaseModel):
    session_name: str
    date_recorded: datetime
    subject_id: str

class BCISessionCreate(BCISessionBase):
    pass

class BCISession(BCISessionBase):
    id: int
    data_points: List[BCIData] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None