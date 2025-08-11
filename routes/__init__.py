from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def get_record(db, Model, _id, model_name="Record", id_field="id"):
    """Get a record by ID or custom field name."""
    if id_field == "id":
        record = db.query(Model).filter(Model.id == _id).first()
    elif id_field == "number":
        record = db.query(Model).filter(Model.number == _id).first()
    else:
        # Generic approach for other field names
        field = getattr(Model, id_field)
        record = db.query(Model).filter(field == _id).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"{model_name} not found")
    return record

def get_records(db, Model, limit: int, offset: int = 0):
    """Get multiple records with limit and offset support."""
    query = db.query(Model)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()

def create_record(db, new_record):
    """Create a new record in the database."""
    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Record already exists or violates constraints")

def update_record(db, Model, schema, id_field="id"):
    record = None
    if id_field == "id":
        record = get_record(db, Model, schema.id, Model.__name__)
    elif id_field == "number":
        record = get_record(db, Model, schema.number, Model.__name__, "number")

    for field, value in schema.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record

def delete_record(db, record):
    try:
        db.delete(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Record cannot be deleted. Error: " + str(e)
        )
    return {"message": "Record deleted successfully"}
