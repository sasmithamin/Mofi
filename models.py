from pydantic import BaseModel
from datetime import date

class Person(BaseModel):
    name: str
    dob: date
    description: str