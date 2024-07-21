from datetime import datetime, timedelta
from sqlalchemy import extract, or_, select, update

from src.contacts.models import Contact
from src.contacts.schemas import ContactsCreate


class ContactsRepository:
    def __init__(self, session):
        self.session = session

    def get_contacts(self, limit: int = 10, offset: int = 0):
        query = select(Contact).limit(limit).offset(offset)
        results = self.session.execute(query)
        return results.scalars().all()

    def create_contacts(self, contact: ContactsCreate):
        new_contact = Contact(**contact.model_dump())
        self.session.add(new_contact)
        self.session.commit()
        self.session.refresh(new_contact)  # To get the ID from the database
        return new_contact

    def search_contacts(self, query):
        q = select(Contact).filter(
            (Contact.first_name.ilike(query))
            | (Contact.last_name.ilike(query))
            | (Contact.email.ilike(query))
        )
        results = self.session.execute(q)
        return results.scalars().all()

    def delete_contact(self, contact_id: int):
        q = select(Contact).where(Contact.id == contact_id)
        result = self.session.execute(q)
        contact = result.scalar_one()
        self.session.delete(contact)
        self.session.commit()

    def get_upcoming_birthdays(self, days: int = 7):
        today = datetime.today()
        upcoming_date = today + timedelta(days=days)
        today_day_of_year = today.timetuple().tm_yday
        upcoming_day_of_year = upcoming_date.timetuple().tm_yday

        if today_day_of_year <= upcoming_day_of_year:
            query = select(Contact).filter(
                extract("doy", Contact.birthday).between(
                    today_day_of_year, upcoming_day_of_year
                )
            )
        else:
            query = select(Contact).filter(
                or_(
                    extract("doy", Contact.birthday) >= today_day_of_year,
                    extract("doy", Contact.birthday) <= upcoming_day_of_year,
                )
            )

        results = self.session.execute(query)
        return results.scalars().all()

    def find_contact(self, identifier: str):
        try:
            contact_id = int(identifier)
        except ValueError:
            contact_id = None

        query = select(Contact).filter(
            or_(
                Contact.id == contact_id,
                Contact.email == identifier,
                Contact.first_name == identifier,
                (Contact.first_name + " " + Contact.last_name) == identifier
            )
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def update_contact(self, identifier: str, contact_update: ContactsCreate):
        contact = self.find_contact(identifier)
        if not contact:
            return None
        stmt = (
            update(Contact)
            .where(Contact.id == contact.id)
            .values(contact_update.model_dump(exclude_unset=True))
            .returning(Contact)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_contact = result.scalar()
        return updated_contact