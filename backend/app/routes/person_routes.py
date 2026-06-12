from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.person import Person
from app.schemas.person_schema import PersonCreate, PersonUpdate

router = APIRouter(prefix="/people", tags=["People"])


def ok(message, data=None):
    return {"success": True, "message": message, "data": data}


@router.post("/create")
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    person = Person(**payload.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return ok("Created successfully", person)


@router.get("")
def list_people(person_type: str | None = None, category_program: str | None = None, batch_name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Person)
    if person_type:
        query = query.filter(Person.person_type == person_type)
    if category_program:
        query = query.filter(Person.category_program == category_program)
    if batch_name:
        query = query.filter(Person.batch_name == batch_name)
    return ok("People fetched", query.order_by(Person.created_at.desc()).all())


@router.get("/{person_id}")
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    return ok("Person fetched", person)


@router.put("/{person_id}")
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(person, key, value)
    db.commit()
    db.refresh(person)
    return ok("Updated successfully", person)


@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    db.delete(person)
    db.commit()
    return ok("Deleted successfully")
