from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class ContactsBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: str | None = None


class ContactsResponse(ContactsBase):
    id: int


class ContactsCreate(ContactsBase):
    pass


# class ContactsUpdate(ContactsBase):
#     done: bool

# class ContactsStatusUpdate(BaseModel):
#     done: bool
