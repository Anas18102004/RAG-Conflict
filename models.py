from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class TimeSlot(BaseModel):
    day: str
    start: str
    end: str

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    timezone: str
    availability: List[TimeSlot]

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Constraint(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: int
    preferred_times: List[TimeSlot]
    unavailable_slots: List[TimeSlot]
    capacity: int

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Event(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    start: datetime
    end: datetime
    priority: int
    participants: List[str]

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Pydantic models for API
class UserSchema(BaseModel):
    id: Optional[int]
    name: str
    timezone: str
    availability: List[dict]
    class Config:
        orm_mode = True

class EventSchema(BaseModel):
    id: Optional[int]
    title: str
    start: str
    end: str
    priority: int
    participants: List[int]
    class Config:
        orm_mode = True

class ConstraintSchema(BaseModel):
    id: Optional[int]
    user_id: int
    preferred_times: List[dict]
    unavailable_slots: List[dict]
    capacity: Optional[int]
    class Config:
        orm_mode = True 