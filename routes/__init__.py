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

def get_records(db, Model, limit: int):
    if limit > 0:
        return db.query(Model).order_by(Model.id.desc()).limit(limit).all().sort(reverse=True)
    elif limit == 0:
        return db.query(Model).all()
    else:
        raise HTTPException(
            status_code=400,
            detail="Limit must be a non-negative integer."
        )

def create_record(db, object):
    db.add(object)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Can't create a new record with that values."
        )

    db.refresh(object)
    return object

def update_record(db, Model, schema):
    record = get_record(db, Model, schema.id)

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