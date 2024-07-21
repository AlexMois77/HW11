from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from src.contacts.repo import ContactsRepository
from src.contacts.schemas import ContactsCreate, ContactsResponse

router = APIRouter()


@router.get("/ping")
def hello():
    return {"message": "pong"}


@router.post("/", response_model=ContactsResponse)
def create_contacts(contact: ContactsCreate, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    return repo.create_contacts(contact)


@router.get("/", response_model=list[ContactsResponse])
def get_contacts(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    return repo.get_contacts(limit, offset)


@router.get("/search/", response_model=list[ContactsResponse])
def search_contacts(query: str, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    return repo.search_contacts(query)


@router.delete("{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    repo.delete_contact(contact_id)
    return {"message": f"Contact {contact_id} deleted"}


@router.get("/contacts/upcoming_birthdays/")
def get_upcoming_birthdays(days: int = 7, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    return repo.get_upcoming_birthdays(days)


@router.put("/{identifier}", response_model=ContactsResponse)
def update_contact(identifier: str, contact_update: ContactsCreate, db: Session = Depends(get_db)):
    repo = ContactsRepository(db)
    updated_contact = repo.update_contact(identifier, contact_update)
    if updated_contact:
        return updated_contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")
